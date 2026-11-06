#!/bin/zsh
# Records raw footage of each toy from a Debug build of the app, played by its own auto-play
# flags. Debug-only flags: nothing here touches the app repo or what ships.
#
#   git clone ~/dev/apple-watch/fidget-app raw/clone (from main), apply tools/capture.patch there
#   (footage-only tweaks, never pushed: a gentle wrist rock, finger jabs in Orbs and Magnet, a
#   faster Pop, a Memory auto-player, a later Dominoes start and a human-speed Trace), build FidgetWatch for watchsimulator, copy the .app to
#   raw/FidgetWatch.app, then:
#   tools/capture.sh [seconds] [toy ...]
#
# Output: raw/<toy>.mov at 422x514. Then run tools/clips.swift to make the loops.
cd "${0:A:h}/.."
U=$(xcrun simctl list devices available | grep "Apple Watch Ultra 3 (49mm)" | head -1 | sed -E 's/.*\(([0-9A-F-]{36})\).*/\1/')
B=com.paulmessenger.fidget.watchkitapp
secs=${1:-20}; shift 2>/dev/null
typeset -A flags
flags=(
  magnet    "-autojab -demo"
  orbs      "-autojab -demo"
  fireworks "-autofireworks"
  pop       "-autopop"
  smoke     "-autosmoke"
  maze      "-autospin -autowin"
  lava      "-autolava"
  trace     "-autotrace"
  bath      "-autobath"
  liquid    "-demo -autowaves -autojab"
  cascade   "-autocascade"
  bagatelle "-autolaunch -autowind"
  dominoes  "-autotopple"
  memory    "-automemory"
  cog       "-autocog"
)
toys=($@); (( $#toys )) || toys=(${(k)flags})
booted=$(xcrun simctl list devices booted | grep -c "$U")
if (( ! booted )); then xcrun simctl boot $U; xcrun simctl bootstatus $U >/dev/null 2>&1; fi
xcrun simctl install $U raw/FidgetWatch.app
for t in $toys; do
  for attempt in 1 2 3; do
    xcrun simctl terminate $U $B 2>/dev/null
    # A press of the crown first: simctl sometimes launches the app suspended otherwise.
    xcrun simctl launch $U $B -unlocked -screenshot -open $t ${=flags[$t]} >/dev/null
    sleep ${WARM:-4}
    xcrun simctl io $U recordVideo --codec=h264 --force raw/$t.mov >/dev/null 2>&1 &
    p=$!; sleep $secs; kill -INT $p; wait $p
    size=$(stat -f %z raw/$t.mov)
    echo "$t attempt $attempt: $size bytes"
    (( size > 150000 )) && break
    # A frozen recording means the simulator dozed: reboot it.
    xcrun simctl shutdown $U; xcrun simctl boot $U; xcrun simctl bootstatus $U >/dev/null 2>&1
  done
done
xcrun simctl terminate $U $B 2>/dev/null
(( booted )) || xcrun simctl shutdown $U
echo done; xcrun simctl list devices booted | grep -c Booted
