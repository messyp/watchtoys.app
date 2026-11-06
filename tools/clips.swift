import AVFoundation
import AppKit
import CoreVideo
import Foundation
setbuf(stdout, nil)

// Turns raw Simulator footage (tools/capture.sh) into the site's loops:
//   swift tools/clips.swift raw assets/clips [--secs 8] [toy ...]
// Each clip is a silent 30 fps H.264 MP4 with the index at the front. The clock and no-phone
// icon are painted out of every frame, the liveliest stretch with no hitches is chosen, and the
// last frames dissolve into the first so the loop has no seam and no fade from black.
// CLIPSTART_<toy>=<seconds> and CLIPSECS_<toy>=<seconds> set a toy's window by hand; BITRATE
// overrides the 2 Mb/s default.

let args = Array(CommandLine.arguments.dropFirst())
let rawDir = args[0], outDir = args[1]
var secs = 8.0
var toys: [String] = []
var i = 2
while i < args.count {
    if args[i] == "--secs" { secs = Double(args[i + 1])!; i += 2 } else { toys.append(args[i]); i += 1 }
}
if toys.isEmpty {
    toys = try! FileManager.default.contentsOfDirectory(atPath: rawDir)
        .filter { $0.hasSuffix(".mov") }.map { String($0.dropLast(4)) }.sorted()
}
let fps = 30, W = 422, H = 514
// Where the clock and no-phone icon sit on the Ultra, top-left origin (from tools/shoot.sh).
let box = (x0: 268, x1: 396, y0: 33, y1: 78)

// Finds the clock and icon's own pixels across the chosen stretch: whatever stays bright white or
// status-icon red there. Only those are repainted, so the toy behind them stays sharp.
// `pad` is how far the repaint reaches past the glyphs: wide clears the clock's soft halo on smooth
// toys, tight keeps hard edges sharp on toys like Bagatelle (MASKPAD_<toy>=3).
func clockMask(_ frames: [Data], pad: Int) -> [Bool] {
    let bw = box.x1 - box.x0 + 1, bh = box.y1 - box.y0 + 1
    var hits = [Int](repeating: 0, count: bw * bh)
    for f in frames {
        f.withUnsafeBytes { (p: UnsafeRawBufferPointer) in
            for y in 0..<bh { for x in 0..<bw {
                let o = ((y + box.y0) * W + x + box.x0) * 4
                let b = Int(p[o]), g = Int(p[o + 1]), r = Int(p[o + 2])
                let inIcon = x + box.x0 < 312      // the red no-phone icon is left of the digits
                if min(r, g, b) > 205 || (inIcon && r > 170 && g < 110 && b < 110) { hits[y * bw + x] += 1 }
            } }
        }
    }
    // A fifth of the frames is enough, so both digits count if the minute changes mid-clip.
    let raw = hits.map { $0 * 5 >= frames.count }
    var mask = raw
    for y in 0..<bh { for x in 0..<bw where raw[y * bw + x] {
        for dy in -pad...pad { for dx in -pad...pad {
            let nx = x + dx, ny = y + dy
            if nx >= 0, ny >= 0, nx < bw, ny < bh { mask[ny * bw + nx] = true }
        } }
    } }
    return mask
}

// Fills the masked pixels from their surroundings, smoothly in both directions.
func inpaint(_ p: UnsafeMutablePointer<UInt8>, mask: [Bool]) {
    let bw = box.x1 - box.x0 + 1, bh = box.y1 - box.y0 + 1
    for c in 0..<3 {
        var v = [Float](repeating: 0, count: (bw + 2) * (bh + 2))
        for y in 0..<(bh + 2) { for x in 0..<(bw + 2) {
            v[y * (bw + 2) + x] = Float(p[((y + box.y0 - 1) * W + x + box.x0 - 1) * 4 + c])
        } }
        let idx: [(Int)] = (0..<(bw * bh)).filter { mask[$0] }.map { i in (i / bw + 1) * (bw + 2) + i % bw + 1 }
        // Start each from the row's average so the smoothing has less far to travel.
        for i in idx { v[i] = (v[i - (i % (bw + 2))] + v[i - (i % (bw + 2)) + bw + 1]) / 2 }
        for _ in 0..<90 {
            for i in idx { v[i] = (v[i - 1] + v[i + 1] + v[i - bw - 2] + v[i + bw + 2]) / 4 }
        }
        for i in idx {
            let y = i / (bw + 2), x = i % (bw + 2)
            p[((y + box.y0 - 1) * W + x + box.x0 - 1) * 4 + c] = UInt8(max(0, min(255, v[i])))
        }
    }
}

for toy in toys {
    autoreleasepool {
        let url = URL(fileURLWithPath: "\(rawDir)/\(toy).mov")
        let asset = AVURLAsset(url: url)
        guard let track = asset.tracks(withMediaType: .video).first else { print("\(toy): no video"); return }
        let reader = try! AVAssetReader(asset: asset)
        let output = AVAssetReaderTrackOutput(track: track, outputSettings: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
        output.alwaysCopiesSampleData = false
        reader.add(output); reader.startReading()

        // Resample to a steady 30 fps, repeating the nearest earlier source frame.
        var frames: [Data] = []
        var stamps: [Double] = []
        var origin: Double?
        var next = 0.0
        while let s = output.copyNextSampleBuffer() {
            guard let pb = CMSampleBufferGetImageBuffer(s) else { continue }
            let t = CMSampleBufferGetPresentationTimeStamp(s).seconds
            if origin == nil { origin = t }
            let at = t - origin!
            stamps.append(at)
            guard at + 0.0001 >= next else { continue }
            CVPixelBufferLockBaseAddress(pb, .readOnly)
            let row = CVPixelBufferGetBytesPerRow(pb)
            var d = Data(count: W * H * 4)
            let src = CVPixelBufferGetBaseAddress(pb)!.assumingMemoryBound(to: UInt8.self)
            d.withUnsafeMutableBytes { (b: UnsafeMutableRawBufferPointer) in
                let dst = b.bindMemory(to: UInt8.self).baseAddress!
                for y in 0..<H { memcpy(dst + y * W * 4, src + y * row, W * 4) }
            }
            CVPixelBufferUnlockBaseAddress(pb, .readOnly)
            while next <= at { frames.append(d); next += 1.0 / Double(fps) }
        }

        // Score each frame: motion overall, minus motion crossing the painted box's edges
        // (which would show as a smear). Hitches disqualify a window.
        func diff(_ a: Data, _ b: Data, _ x0: Int, _ x1: Int, _ y0: Int, _ y1: Int) -> Double {
            var sum = 0, n = 0
            a.withUnsafeBytes { (pa: UnsafeRawBufferPointer) in b.withUnsafeBytes { (pb: UnsafeRawBufferPointer) in
                var y = y0
                while y < y1 { var x = x0
                    while x < x1 { let o = (y * W + x) * 4 + 1; sum += abs(Int(pa[o]) - Int(pb[o])); n += 1; x += 6 }
                    y += 6 }
            }}
            return Double(sum) / Double(max(n, 1))
        }
        var motion = [0.0], edge = [0.0], light = [0.0]
        let black = Data(count: W * H * 4)
        for f in 1..<frames.count {
            motion.append(diff(frames[f], frames[f - 1], 0, W, 0, H))
            edge.append(diff(frames[f], frames[f - 1], box.x0 - 8, box.x1 + 8, box.y0, box.y1))
            light.append(diff(frames[f], black, 0, W, 0, H))
        }
        var hitch = [Bool](repeating: false, count: frames.count)
        for (a, b) in zip(stamps, stamps.dropFirst()) where b - a > 0.07 {
            let f = Int(a * Double(fps)); if f < hitch.count { hitch[f] = true; if f + 1 < hitch.count { hitch[f + 1] = true } }
        }
        let thisSecs = ProcessInfo.processInfo.environment["CLIPSECS_\(toy)"].flatMap(Double.init) ?? secs
        let w = min(Int(thisSecs * Double(fps)), frames.count - 1)
        var bestAt = 0, best = -Double.infinity
        let forced = ProcessInfo.processInfo.environment["CLIPSTART_\(toy)"].flatMap(Double.init)
        var at = 0
        while at + w < frames.count {
            let range = at..<(at + w)
            var s = range.reduce(0) { $0 + motion[$1] } / Double(w)
            s -= range.reduce(0) { $0 + edge[$1] } / Double(w) * 0.5
            // The opening frame must have something on it: no dark first frame.
            s += min(light[at], 40) * 0.25
            if range.contains(where: { hitch[$0] }) { s -= 1000 }
            if s > best { best = s; bestAt = at }
            at += 3
        }
        if let forced { bestAt = min(Int(forced * Double(fps)), frames.count - w - 1) }
        let hitches = (bestAt..<(bestAt + w)).filter { hitch[$0] }.count
        var clip = Array(frames[bestAt..<(bestAt + w)])
        let mask = clockMask(clip, pad: ProcessInfo.processInfo.environment["MASKPAD_\(toy)"].flatMap(Int.init) ?? 6)
        for n in clip.indices {
            clip[n].withUnsafeMutableBytes { (b: UnsafeMutableRawBufferPointer) in
                inpaint(b.bindMemory(to: UInt8.self).baseAddress!, mask: mask)
            }
        }

        // Write it: the last third of a second dissolves into the opening frames, which are skipped.
        let out = URL(fileURLWithPath: "\(outDir)/\(toy).mp4")
        try? FileManager.default.removeItem(at: out)
        let writer = try! AVAssetWriter(outputURL: out, fileType: .mp4)
        writer.shouldOptimizeForNetworkUse = true
        let rate = Int(ProcessInfo.processInfo.environment["BITRATE"] ?? "") ?? 2_000_000
        let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
            AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
            AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: rate,
                AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
                AVVideoExpectedSourceFrameRateKey: fps, AVVideoMaxKeyFrameIntervalKey: fps * 2]])
        input.expectsMediaDataInRealTime = false
        let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
            kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
        writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
        let fade = fps * 2 / 3
        for n in fade..<clip.count {
            autoreleasepool {
                while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
                var pbo: CVPixelBuffer?
                CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pbo)
                let pb = pbo!
                CVPixelBufferLockBaseAddress(pb, [])
                let row = CVPixelBufferGetBytesPerRow(pb)
                let dst = CVPixelBufferGetBaseAddress(pb)!.assumingMemoryBound(to: UInt8.self)
                let into = n - (clip.count - fade)
                let al = into >= 0 ? Double(into + 1) / Double(fade + 1) : 0
                clip[n].withUnsafeBytes { (a: UnsafeRawBufferPointer) in
                    if into >= 0 {
                        clip[into].withUnsafeBytes { (b: UnsafeRawBufferPointer) in
                            for y in 0..<H {
                                let q = dst + y * row
                                for x in 0..<(W * 4) {
                                    let o = y * W * 4 + x
                                    q[x] = UInt8(Double(a[o]) * (1 - al) + Double(b[o]) * al)
                                }
                            }
                        }
                    } else {
                        for y in 0..<H { memcpy(dst + y * row, a.baseAddress! + y * W * 4, W * 4) }
                    }
                }
                CVPixelBufferUnlockBaseAddress(pb, [])
                adaptor.append(pb, withPresentationTime: CMTime(value: CMTimeValue(n - fade), timescale: CMTimeScale(fps)))
            }
        }
        input.markAsFinished()
        let done = DispatchSemaphore(value: 0)
        writer.finishWriting { done.signal() }
        done.wait()

        // The poster is the finished clip's own first frame, so the page doesn't jump when it starts.
        let made = AVURLAsset(url: out)
        let gen = AVAssetImageGenerator(asset: made)
        gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
        let cg = try! gen.copyCGImage(at: .zero, actualTime: nil)
        try! NSBitmapImageRep(cgImage: cg).representation(using: .jpeg, properties: [.compressionFactor: 0.85])!
            .write(to: URL(fileURLWithPath: "\(outDir)/\(toy).jpg"))
        let bytes = (try! FileManager.default.attributesOfItem(atPath: out.path)[.size] as! Int)
        print("\(toy): start \(Double(bestAt) / Double(fps))s, \(Double(bytes) / 1_048_576) MB, hitches \(hitches), status \(writer.status.rawValue)")
    }
}
