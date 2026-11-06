import AVFoundation
import AppKit
import CoreVideo
import Foundation
setbuf(stdout, nil)

// Cuts the hero's one looping film from the finished toy clips, so the hero plays a single file
// and never has to swap sources on a phone:
//   hero <clips dir> <out.mp4> [--secs 2.6] [--fade 0.33] toy[:start] ...
//   hero <clips dir> <sheet.jpg> --sheet toy ...     a contact sheet of each toy's liveliest stretch
// Each toy gets its liveliest stretch unless :start gives one in seconds. Each dissolves into the
// next, and the last dissolves into the first, so the loop has no seam. BITRATE overrides 1.5 Mb/s.

let args = Array(CommandLine.arguments.dropFirst())
let clipsDir = args[0], outPath = args[1]
var secs = 2.6, fade = 0.33, sheet = false
var picks: [(toy: String, start: Double?)] = []
var i = 2
while i < args.count {
    switch args[i] {
    case "--secs": secs = Double(args[i + 1])!; i += 2
    case "--fade": fade = Double(args[i + 1])!; i += 2
    case "--sheet": sheet = true; i += 1
    default:
        let p = args[i].split(separator: ":")
        picks.append((String(p[0]), p.count > 1 ? Double(p[1]) : nil)); i += 1
    }
}
let fps = 30, W = 422, H = 514
let L = Int((secs * Double(fps)).rounded()), F = Int((fade * Double(fps)).rounded())
let need = L + F

func frames(_ toy: String) -> [Data] {
    let asset = AVURLAsset(url: URL(fileURLWithPath: "\(clipsDir)/\(toy).mp4"))
    let track = asset.tracks(withMediaType: .video)[0]
    let reader = try! AVAssetReader(asset: asset)
    let output = AVAssetReaderTrackOutput(track: track, outputSettings: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
    reader.add(output)
    reader.startReading()
    var out: [Data] = []
    while let s = output.copyNextSampleBuffer(), let b = CMSampleBufferGetImageBuffer(s) {
        CVPixelBufferLockBaseAddress(b, .readOnly)
        let base = CVPixelBufferGetBaseAddress(b)!.assumingMemoryBound(to: UInt8.self)
        let row = CVPixelBufferGetBytesPerRow(b)
        var d = Data(count: W * H * 4)
        d.withUnsafeMutableBytes { (p: UnsafeMutableRawBufferPointer) in
            for y in 0..<H { memcpy(p.baseAddress! + y * W * 4, base + y * row, W * 4) }
        }
        CVPixelBufferUnlockBaseAddress(b, .readOnly)
        out.append(d)
    }
    return out
}

// How much changed from one frame to the next, on a sparse grid.
func liveliest(_ f: [Data]) -> Int {
    var motion = [Double](repeating: 0, count: f.count)
    for n in 1..<f.count {
        var sum = 0
        f[n].withUnsafeBytes { (a: UnsafeRawBufferPointer) in
            f[n - 1].withUnsafeBytes { (b: UnsafeRawBufferPointer) in
                for y in stride(from: 90, to: H, by: 6) { for x in stride(from: 0, to: W, by: 6) {
                    let o = (y * W + x) * 4 + 1
                    sum += abs(Int(a[o]) - Int(b[o]))
                } }
            }
        }
        motion[n] = Double(sum)
    }
    var best = 0, bestScore = -1.0
    for s in 0...(f.count - need) {
        let score = motion[s..<(s + need)].reduce(0, +)
        if score > bestScore { best = s; bestScore = score }
    }
    return best
}

func image(_ d: Data) -> CGImage {
    let provider = CGDataProvider(data: d as CFData)!
    return CGImage(width: W, height: H, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: W * 4,
                   space: CGColorSpaceCreateDeviceRGB(),
                   bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue),
                   provider: provider, decode: nil, shouldInterpolate: true, intent: .defaultIntent)!
}

if sheet {
    let across = 5, tw = W / 2, th = H / 2
    let ctx = CGContext(data: nil, width: across * tw, height: picks.count * th, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    for (r, p) in picks.enumerated() {
        let f = frames(p.toy), s = p.start.map { Int($0 * Double(fps)) } ?? liveliest(f)
        print(p.toy, "best start", Double(s) / Double(fps), "of", Double(f.count) / Double(fps))
        for c in 0..<across {
            let d = f[s + c * (need - 1) / (across - 1)]
            ctx.draw(image(d), in: CGRect(x: c * tw, y: (picks.count - 1 - r) * th, width: tw, height: th))
        }
    }
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
    try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8])!.write(to: URL(fileURLWithPath: outPath))
    exit(0)
}

var segs: [[Data]] = []
for p in picks {
    let f = frames(p.toy), s = p.start.map { Int($0 * Double(fps)) } ?? liveliest(f)
    print(p.toy, "from", Double(s) / Double(fps))
    segs.append(Array(f[s..<(s + need)]))
}

// Start just past the dissolve into the first toy, so frame one and the poster are one clean toy.
var seq: [(Data, Data?, Double)] = []
for k in 0..<segs.count {
    for n in F..<L { seq.append((segs[k][n], nil, 0)) }
    let next = segs[(k + 1) % segs.count]
    for n in 0..<F {
        let t = Double(n + 1) / Double(F + 1)
        seq.append((segs[k][L + n], next[n], t * t * (3 - 2 * t)))
    }
}

let url = URL(fileURLWithPath: outPath)
try? FileManager.default.removeItem(at: url)
let writer = try! AVAssetWriter(outputURL: url, fileType: .mp4)
writer.shouldOptimizeForNetworkUse = true
let rate = Int(ProcessInfo.processInfo.environment["BITRATE"] ?? "") ?? 1_500_000
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: rate,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
        AVVideoMaxKeyFrameIntervalKey: fps * 2]])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)
for (n, step) in seq.enumerated() {
    while !input.isReadyForMoreMediaData { usleep(1000) }
    var pb: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pb)
    let b = pb!
    CVPixelBufferLockBaseAddress(b, [])
    let dst = CVPixelBufferGetBaseAddress(b)!.assumingMemoryBound(to: UInt8.self)
    let row = CVPixelBufferGetBytesPerRow(b)
    let m = Int(step.2 * 256)
    step.0.withUnsafeBytes { (a: UnsafeRawBufferPointer) in
        for y in 0..<H {
            let d = dst + y * row, ao = y * W * 4
            if let other = step.1 {
                other.withUnsafeBytes { (c: UnsafeRawBufferPointer) in
                    for x in 0..<(W * 4) { d[x] = UInt8((Int(a[ao + x]) * (256 - m) + Int(c[ao + x]) * m) >> 8) }
                }
            } else {
                memcpy(d, a.baseAddress! + ao, W * 4)
            }
        }
    }
    CVPixelBufferUnlockBaseAddress(b, [])
    adaptor.append(b, withPresentationTime: CMTime(value: CMTimeValue(n), timescale: CMTimeScale(fps)))
}
input.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
if writer.status != .completed { print("failed:", writer.error as Any); exit(1) }

// The poster is the finished film's first frame, so it matches what plays.
let gen = AVAssetImageGenerator(asset: AVURLAsset(url: url))
gen.requestedTimeToleranceBefore = .zero
gen.requestedTimeToleranceAfter = .zero
let first = try! gen.copyCGImage(at: .zero, actualTime: nil)
let jpg = NSBitmapImageRep(cgImage: first).representation(using: .jpeg, properties: [.compressionFactor: 0.82])!
try! jpg.write(to: url.deletingPathExtension().appendingPathExtension("jpg"))
let size = (try! FileManager.default.attributesOfItem(atPath: outPath)[.size] as! NSNumber).intValue
print("wrote", outPath, seq.count, "frames,", String(format: "%.1f s, %.2f MB", Double(seq.count) / Double(fps), Double(size) / 1_048_576))
