#!/usr/bin/env bash
# ARCHIVED AS RUN: paths refer to the original ~/rnaseq-obob layout (config files were beside this script).
# One-time scheduled resume of the nf-core/rnaseq run (invoked by cron).
# Relaunches run_pipeline.sh (which already has -resume baked in), detached the same
# way the original run was: setsid+nohup so it survives independent of cron's own session.
set -uo pipefail

LOGDIR="$HOME/nf-work/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/pause_resume.log"
stamp() { date +"%Y-%m-%d %H:%M:%S %Z"; }

echo "[$(stamp)] Scheduled resume triggered." >> "$LOG"

cd "$HOME/rnaseq-obob"
RUNLOG="$LOGDIR/run_$(date +%Y%m%d_%H%M%S)_resumed.log"
setsid nohup bash run_pipeline.sh > "$RUNLOG" 2>&1 < /dev/null &
disown

echo "[$(stamp)] Relaunched with -resume. New run log: $RUNLOG" >> "$LOG"
