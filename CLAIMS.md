# Claims on the page

Checked on 6 November 2026 against commit f5ecb7b of fidget-app and `AppStore/LISTING.md`. There's no live App Store page yet, so recheck these against it at launch.

| Claim | Source |
|---|---|
| Fifteen toys | `ObjectKind.shown` in HomeView.swift has 15 |
| Five free: Magnet, Orbs, Pop, Maze, Trace | `isFree` in HomeView.swift |
| Try each locked toy free, twice, for a minute at a time | `tries = 2`, `trialSeconds = 60` in UnlockView.swift |
| One purchase unlocks them all, plus every toy added later | LISTING.md; Paul's decision, 19 October |
| Family Sharing included | LISTING.md (in-app purchase set up with Family Sharing on) |
| No ads, no subscription, no account, no data collected | LISTING.md; App Privacy is "Data Not Collected" |
| A finger jabs the beads and pushes them about (Orbs) | `touchMoved` in PhysicsObject.swift sets the world's pusher on a real watch; Paul's own description |
| Balls fly to your finger with sparks and scatter on release (Magnet) | `fingerPull` in MagnetSim.swift and World.swift; Paul's own description |
| Flick the boat with a finger (Liquid) | OrbsSim.swift: a finger near the boat flicks and spins it |
| Hundreds of beads (Orbs) | default `count` is 300 in OrbsSim.swift |
| 25 shapes (Trace) | `TraceSim.shapes` has 25 |
| Ten bubbles (Memory) | `padRows = [3, 4, 3]` in PopSim.swift |
| Walnut labyrinths and stone castle keeps (Maze) | MazeSim.swift |
| Peonies, rings, willows, palms, chrysanthemums (Fireworks) | `Style` in FireworksSim.swift |
| Wind with the Digital Crown, flick to fire (Bagatelle) | BagatelleSim.swift hint card |
| Haptic strength, colours, sizes and more in Settings | LISTING.md; SettingsView.swift |
| Prefer bubble wrap? It's in Settings | LISTING.md |
| Coming soon to the App Store | iTunes lookup returned nothing for both bundle IDs on 6 November |

Not printed, on purpose: price, version, download size, App Store ID.
