#!/usr/bin/env bash
# ARCHIVED AS RUN: paths refer to the original ~/rnaseq-obob layout (config files were beside this script).
# One-time scheduled pause of the nf-core/rnaseq run (invoked by cron).
# Cleanly terminates the whole process tree (Nextflow orchestrator, Apptainer containers,
# squashfuse mounts, task subprocesses) via its shared session ID, so nothing is left
# consuming CPU/RAM. Safe to resume later with `-resume` (already in run_pipeline.sh) —
# only whatever task was actively mid-run at this exact moment needs to redo that one step.
set -uo pipefail

LOGDIR="$HOME/nf-work/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/pause_resume.log"
stamp() { date +"%Y-%m-%d %H:%M:%S %Z"; }

echo "[$(stamp)] Scheduled pause triggered." >> "$LOG"

PID=$(pgrep -f "nextflow-25.04.7-one.jar" | head -1)
if [ -z "$PID" ]; then
    echo "[$(stamp)] No running nextflow process found — nothing to pause." >> "$LOG"
    exit 0
fi

SID=$(ps -o sid= -p "$PID" | tr -d ' ')
echo "[$(stamp)] Found nextflow PID=$PID SID=$SID. Sending SIGTERM to full session." >> "$LOG"
pkill -TERM -s "$SID"

sleep 20
REMAINING=$(pgrep -s "$SID" | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "[$(stamp)] $REMAINING process(es) still alive after SIGTERM, sending SIGKILL." >> "$LOG"
    pkill -KILL -s "$SID"
    sleep 3
fi

REMAINING=$(pgrep -s "$SID" | wc -l)
echo "[$(stamp)] Pause complete. Remaining processes in session: $REMAINING" >> "$LOG"
