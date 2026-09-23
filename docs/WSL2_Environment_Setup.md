# WSL2 Environment Setup — Lab PC Reference

*Lab PC (domain: EKMD, user: `govindp`) — Windows host, Linux (WSL2/Ubuntu) analysis environment.*
*Write-once reference: machine/environment setup, not tied to any specific analysis. See `RNAseq_Analysis_Pipeline.md` for the actual RNA-seq workflow.*

## Hardware / environment facts
- CPU: Intel Xeon w3-2435, 8 cores / 16 threads. RAM: 256 GB total.
- `C:` = **Samsung NVMe SSD**, 2 TB (1.4 TB free) — fast random I/O.
- `D:` = **Toshiba MG11ACA2 HDD in RAID**, "New Volume", 22.3 TB (10.3 TB free) — high capacity, slow random I/O.
- **Decision: WSL2's virtual disk and all active working/compute data live on `C:` (NVMe)**, not `D:`. `D:` is spinning disk and would bottleneck aligners (e.g. STAR) that do heavy random I/O. `D:` is used only as bulk/cold storage for raw originals and final results.
- WSL2 distro storage itself (the `ext4.vhdx` backing Ubuntu) lives under `C:\Users\govindp\AppData\Local\Packages\CanonicalGroupLimited...\LocalState\`. Why: `wsl --install` installs Ubuntu as a **Microsoft Store package (MSIX/UWP)**, and Windows enforces this exact storage location for every Store app (not WSL-specific) — an isolated, non-human-named folder ID'd by a machine-generated package identifier, under `Local` (not `Roaming`, so it never tries to sync over a domain roaming profile) and per-user. It is not human-navigable and not meant to be — all real project paths live *inside* Ubuntu instead (e.g. `~/data/raw/`). This is only mandatory for the default Store-based install; `wsl --import <name> <custom-folder> <tar>` can register a distro under any custom name/location instead, bypassing the Store-app model (not used here — no benefit for this project).
- Ubuntu is registered per-Windows-account. Only `govindp` (personal account, not shared) has it installed. If another Windows login on this PC ever needs it, that's a separate distro/install — not shared automatically. WSL2's underlying platform (kernel, Virtual Machine Platform feature) is machine-wide once enabled, but each distro instance and everything installed inside it is per-account.
- To browse WSL files from Windows Explorer (optional, not needed for actual work): `\\wsl.localhost\Ubuntu\home\govind\...` or run `explorer.exe .` from inside the target Ubuntu directory.
- WSL command quoting gotcha (Windows-side PowerShell only): paths with spaces passed through `wsl bash -lc '...'` from PowerShell should use backslash-escaped spaces (`RNA\ Seq\ OB-OB`), not double quotes — embedded double quotes get mangled between PowerShell and `wsl.exe`'s argv passing. Not relevant once working natively inside Ubuntu.

## Phase 1 — Install WSL2 + Ubuntu ✅ done
- Ubuntu installed and provisioned. Linux user: `govind` (hostname `michaelklabpc2`).
- `sudo apt update && sudo apt upgrade -y` completed (142 packages upgraded).
- GUI apps: WSLg is installed (v1.0.73.2), so individual Linux GUI apps (e.g. IGV, RStudio) run as native-looking windows on the Windows desktop — no full desktop environment needed.

## Phase 2 — Configure resources ✅ done
- `C:\Users\govindp\.wslconfig`:
  ```
  [wsl2]
  processors=14
  memory=224GB
  swap=16GB
  localhostForwarding=true
  ```
  (Leaves 2 threads / ~32 GB for Windows.)
- Applied via `wsl --shutdown` + relaunch. Verified inside Ubuntu: `nproc` → 14, `free -h` → ~220 GiB total, 16 GiB swap.

## Claude Code inside Ubuntu ✅ done
- Installed natively: `curl -fsSL https://claude.ai/install.sh | bash` → v2.1.258, at `~/.local/bin/claude`.
- Added to PATH via `~/.bashrc`.
- Rationale: running Claude Code natively inside Ubuntu (rather than the Windows-side session shelling out via `wsl bash -lc`) gives clean native bash execution, no `/mnt/c` vs `/mnt/d` path confusion, and avoids UTF-16 output-encoding glitches that occur when PowerShell captures `wsl.exe` output.

## Bioinformatics toolchain ✅ done (2026-09-02)
- **`sudo` requires an interactive TTY password in this environment** — `sudo -n true` fails, and a non-interactive shell (e.g. Claude Code's Bash tool) gets `sudo: A terminal is required to authenticate`. Confirmed while trying to `apt install` Java/Apptainer. Workaround used project-wide: install everything user-space via conda-forge/bioconda (Miniforge) instead of `apt`. If a future tool genuinely requires `apt`/root, that install has to be run by the user directly in an interactive terminal (or via the `!` prefix in a Claude Code prompt, which runs in the user's own interactive session).
- **Miniforge** (conda + mamba) installed to `~/miniforge3`, silent/batch install (`Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3`). `conda init bash` run once (added a managed block to `~/.bashrc`, backed up as `~/.bashrc.bak.<timestamp>` first); `conda config --set auto_activate_base false` so new shells don't land in `(base)`.
- **`nfcore` conda env**: `openjdk=21`, `nextflow=25.04.7`, `apptainer=1.5.3`, `nf-core=4.1.0`, installed together from `conda-forge` + `bioconda` so Java/Nextflow/Apptainer versions are mutually consistent. Activate with `conda activate nfcore`.
- **Container backend: Apptainer**, not Docker Desktop. Docker Desktop needs a Windows-side GUI installer (outside what's scriptable from inside Ubuntu) and a running daemon; Apptainer is rootless, needs no daemon, and installs cleanly from conda-forge — simpler fit for this WSL2 setup. `apptainer --version` → 1.5.3, confirmed working.
- **poppler** (`pdftotext`/`pdftoppm`) installed into the conda `base` env — used once to read a Takara PDF manual directly (see `RNAseq_Analysis_Pipeline.md` Phase 0); generally useful for reading any PDF locally going forward.
- Project-specific tool versions/params (Nextflow config, pipeline pin, sample sheet) live in `~/rnaseq-obob/nextflow.config` etc., not here — this section is just "what's installed on the machine."

## Housekeeping — undo / removal
- `wsl --unregister Ubuntu` is the full "undo" if ever needed to remove everything cleanly — doesn't touch Windows or other files.

## Method comparison (for reference — why WSL2 over alternatives)

| Method | Performance | Isolation from Windows | Reproducibility | Setup effort |
|---|---|---|---|---|
| **WSL2 + Ubuntu** (chosen) | Near-native | High — separate virtual disk | High, paired with conda/containers | Low — one command + reboot |
| Docker Desktop (WSL2 backend) | Near-native | Very high — throwaway containers | Highest — pins entire OS+binaries | Low-medium |
| VirtualBox/VMware full VM | Slower (virtualized hardware) | Very high — separate disk image | High if snapshotted | Medium |
| Cloud VM / HPC cluster | Best for very large jobs | Total — nothing local | High if scripted | Medium + ongoing cost |
| Native Windows tools | Fine, but many key tools unsupported | N/A | Lower | Low, but hits missing-tool walls |
| Dual-boot Linux | Native, fastest | None (separate partition) | High | High — most disruptive |
