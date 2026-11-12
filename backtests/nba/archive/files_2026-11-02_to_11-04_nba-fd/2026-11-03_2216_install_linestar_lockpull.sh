#!/bin/zsh
# v1.2b rule 3: second LineStar NBA pull close to lock.
# Adds LaunchAgent com.phong.linestar2 = same command as com.phong.linestar,
# scheduled Mon-Fri 3:45 PM and Saturday 2:45 PM (Mac local time). Nothing on Sunday.
# The existing 3:15 / 2:15 agent is left untouched.
set -e
SRC="$HOME/Library/LaunchAgents/com.phong.linestar.plist"
DST="$HOME/Library/LaunchAgents/com.phong.linestar2.plist"
if [ ! -f "$SRC" ]; then
  echo "STOP: $SRC not found — the 3:15 LineStar agent isn't installed on this Mac."; exit 1
fi
launchctl bootout "gui/$(id -u)" "$DST" 2>/dev/null || true
cp "$SRC" "$DST"
plutil -replace Label -string com.phong.linestar2 "$DST"
plutil -remove StartCalendarInterval "$DST" 2>/dev/null || true
plutil -remove RunAtLoad "$DST" 2>/dev/null || true
plutil -insert StartCalendarInterval -json '[
 {"Weekday":1,"Hour":15,"Minute":45},{"Weekday":2,"Hour":15,"Minute":45},
 {"Weekday":3,"Hour":15,"Minute":45},{"Weekday":4,"Hour":15,"Minute":45},
 {"Weekday":5,"Hour":15,"Minute":45},{"Weekday":6,"Hour":14,"Minute":45}]' "$DST"
plutil -lint "$DST"
echo "Command this agent runs (should be the NBA LineStar pull):"
plutil -extract ProgramArguments json -o - "$DST"; echo
launchctl bootstrap "gui/$(id -u)" "$DST"
launchctl print "gui/$(id -u)/com.phong.linestar2" | grep -E "state|path" | head -3
echo "DONE: second LineStar pull installed — Mon-Fri 3:45 PM, Sat 2:45 PM."
