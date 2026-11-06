# watchtoys.app

The website for Watch Toys: Fidget & Games, an Apple Watch app by Beautiful Distraction. Plain HTML hosted on GitHub Pages, with its CSS and script inline and no build step on the host. `tools/page.py` writes `index.html` from one toy list, so the fifteen toys' copy stays in one place.

## Release state

The app isn't on the App Store yet, so the page shows a "Coming soon to the App Store" label in two places and carries no badge. When it goes live:

1. Confirm the live listing, App Store ID and copy with the iTunes lookup API.
2. Replace the hero's `SOON` with Apple's badge (one per page, at least 40px tall, clear space of a quarter of its height), using `https://apps.apple.com/app/id<ID>`.
3. Make the closing one a text button to the same link.
4. Remove `<meta name="robots" content="noindex">` only when Paul is ready to share the site.

Don't print a price, version or download size. They go stale.

## Assets

- `assets/clips`: silent 30 fps H.264 loops with a poster each. `tools/capture.sh` records the Ultra 3 Simulator; `tools/clips.swift` picks the liveliest stretch with no hitches, paints the clock out and dissolves the tail into the head. `tools/capture.patch` holds footage-only tweaks for a throwaway clone of the app. It stays out of this public repo because it quotes the private app's code, and it must never go to the app repo either.
- `assets/logo.png`, `assets/icon.png`: the app icon as on the App Store, from `AppIcon.appiconset/icon-1024.png` in the app repo. The page shows it in a circle, as watchOS does.
- `assets/apple-watch-ultra-4.png`: Apple's official product bezel, used as supplied. Don't crop, tilt, shadow or overlay it.
- `assets/fonts`: Bricolage Grotesque and Instrument Sans, under the SIL Open Font License 1.1, self-hosted so the site loads nothing from third parties.
- Film slot: the section is commented out in `tools/page.py` until `assets/film` exists.

`assets/clips/hero.mp4` is the hero's one looping film, cut by `tools/hero.swift` from the finished clips of Magnet, Orbs, Pop, Liquid and Lava, so rebuild it after recutting any of those: `swiftc -O tools/hero.swift -o raw/hero && raw/hero assets/clips assets/clips/hero.mp4 magnet orbs pop liquid lava`.

Clip settings used: `CLIPSTART_trace=4.4 CLIPSTART_dominoes=2.2 CLIPSECS_dominoes=5.2 CLIPSTART_pop=16.3 MASKPAD_bagatelle=3 MASKPAD_cog=3 MASKPAD_cascade=3`, with `--secs 8.67`.

`raw/` holds the raw footage and the build, and isn't committed. Every claim on the page is traced in `CLAIMS.md`.
