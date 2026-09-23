#!/usr/bin/env bash
# Copy one group's final results to D: and verify every file's size matches.
# Usage: backup_group.sh <GROUP>
# Only prints "BACKUP VERIFIED" when nothing differs; clean up local files only after that.
set -euo pipefail

GROUP="$1"
SRC="$HOME/results-aging/${GROUP}/"
DEST="/mnt/d/RONI REGGEV/RNA Seq Files/Final Results/${GROUP}/"
stamp() { date +"%Y-%m-%d %H:%M:%S %Z"; }

[ -d "$SRC" ] || { echo "missing $SRC"; exit 1; }
[ -n "$(ls "$SRC"/track_a/*.gene_counts.tsv 2>/dev/null)" ] || { echo "no Track A counts in $SRC; not backing up"; exit 1; }

mkdir -p "$DEST"
echo "=== $(stamp) : rsync ${GROUP} -> D: ==="
# NTFS via drvfs: skip owner/group/perms, compare on size+mtime (with 2s NTFS tolerance)
rsync -rt --modify-window=2 --info=progress2 "$SRC" "$DEST"
cp "$(dirname "${BASH_SOURCE[0]}")/samplesheet_${GROUP}.csv" "$DEST"

echo "=== $(stamp) : verify ==="
diffs=$(rsync -rn --size-only --out-format='%n' "$SRC" "$DEST" | grep -v '/$' || true)
if [ -n "$diffs" ]; then
    echo "BACKUP MISMATCH:"; echo "$diffs"; exit 1
fi
echo "BACKUP VERIFIED ${GROUP}: $(du -sh "$SRC" | cut -f1) local, $(find "$SRC" -type f | wc -l) files"
