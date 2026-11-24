#!/usr/bin/env bash
# Read-only first-boot diagnostic for EdgeInspect-AI on AMD Kria KV260.
# Run as the normal login user; sudo is not required.
set -u

STAMP="$(date +%Y%m%d_%H%M%S 2>/dev/null || echo unknown)"
OUT="${1:-kv260_system_report_${STAMP}.txt}"

{
  echo "EDGEINSPECT-AI | KV260 FIRST-BOOT REPORT"
  echo "Generated: $(date -Is 2>/dev/null || date)"
  echo

  echo "[SYSTEM]"
  for cmd in uname hostname uptime; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "--- $cmd ---"
      "$cmd" 2>&1 || true
    fi
  done
  echo "--- /etc/os-release ---"
  cat /etc/os-release 2>&1 || true
  echo

  echo "[CPU / MEMORY / STORAGE]"
  for cmd in lscpu free df; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "--- $cmd ---"
      case "$cmd" in
        df) df -h 2>&1 || true ;;
        *) "$cmd" 2>&1 || true ;;
      esac
    fi
  done
  echo

  echo "[PYTHON / PACKAGES]"
  if command -v python3 >/dev/null 2>&1; then
    python3 --version 2>&1 || true
    python3 - <<'PY'
import importlib.util, platform, sys
print("python_executable:", sys.executable)
print("python_version:", sys.version.replace("\n", " "))
print("machine:", platform.machine())
for name in ("torch", "torchvision", "ultralytics", "cv2", "numpy", "onnxruntime", "executorch", "gradio"):
    try:
        spec = importlib.util.find_spec(name)
        print(f"{name}:", "available" if spec else "not installed")
    except (ImportError, ValueError) as exc:
        print(f"{name}:", f"check failed ({exc})")
PY
  else
    echo "python3: not found"
  fi
  echo

  echo "[NETWORK]"
  if command -v ip >/dev/null 2>&1; then ip -br addr 2>&1 || true; fi
  if command -v hostname >/dev/null 2>&1; then hostname -I 2>&1 || true; fi
  echo

  echo "[CAMERA / USB DEVICES]"
  if compgen -G '/dev/video*' >/dev/null; then ls -l /dev/video* 2>&1 || true; else echo "No /dev/video* device detected"; fi
  if command -v lsusb >/dev/null 2>&1; then lsusb 2>&1 || true; fi
  echo

  echo "[AMD / PLATFORM UTILITIES]"
  for cmd in platformstats xmutil xrt-smi; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "$cmd: found at $(command -v "$cmd")"
      case "$cmd" in
        platformstats) timeout 5 "$cmd" 2>&1 || true ;;
        xmutil) timeout 5 "$cmd" listapps 2>&1 || true ;;
        xrt-smi) timeout 5 "$cmd" examine 2>&1 || true ;;
      esac
    else
      echo "$cmd: not found"
    fi
  done
  echo
  echo "[END OF REPORT]"
} > "$OUT" 2>&1

printf 'KV260 diagnostic report saved to: %s\n' "$OUT"
printf 'Review the file before sharing; it contains local network/interface details.\n'
