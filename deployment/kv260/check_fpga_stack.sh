#!/usr/bin/env bash
# Read-only inventory for the KV260 FPGA/DPU software stack.
# Does not install packages, load/unload overlays, or alter board settings.
set -u

echo "EDGEINSPECT-AI | KV260 FPGA STACK CHECK"
echo "Generated: $(date -Is 2>/dev/null || date)"
echo

echo "[BOARD / OS]"
uname -a 2>&1 || true
uname -m 2>&1 || true
cat /etc/os-release 2>&1 || true
echo

echo "[PYTHON]"
if command -v python3 >/dev/null 2>&1; then
  python3 --version 2>&1 || true
fi
echo

echo "[ACCELERATOR COMMANDS]"
for name in xmutil xrt-smi xbutil xdputil vai_c; do
  if command -v "$name" >/dev/null 2>&1; then
    printf '%s: %s\n' "$name" "$(command -v "$name")"
  else
    printf '%s: not found\n' "$name"
  fi
done
if command -v xmutil >/dev/null 2>&1; then
  echo "--- xmutil listapps ---"
  timeout 10 xmutil listapps 2>&1 || true
fi
echo

echo "[INSTALLED RUNTIME PACKAGES]"
if command -v dpkg-query >/dev/null 2>&1; then
  dpkg-query -W -f='${binary:Package}\t${Version}\n' \
    'xrt*' 'vart*' 'vitis-ai*' 'pynq*' 'xlnx-firmware*' 2>/dev/null || true
else
  echo "dpkg-query not available"
fi
echo

echo "[PYTHON MODULES]"
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import importlib.util
for name in ("pynq", "vart", "xir", "vai_runtime", "torch", "ultralytics"):
    try:
        print(f"{name}: {'available' if importlib.util.find_spec(name) else 'not installed'}")
    except (ImportError, ValueError) as exc:
        print(f"{name}: lookup failed ({exc})")
PY
fi
echo

echo "[FPGA DEVICES / OVERLAYS]"
if compgen -G '/dev/dri/*' >/dev/null; then ls -l /dev/dri/* 2>&1 || true; else echo "No /dev/dri entries"; fi
if compgen -G '/dev/dpu*' >/dev/null; then ls -l /dev/dpu* 2>&1 || true; else echo "No /dev/dpu* entries"; fi
for dir in /lib/firmware/xilinx /usr/lib/firmware/xilinx /boot/firmware; do
  if [ -d "$dir" ]; then
    echo "--- $dir (names matching DPU / KV260 / K26) ---"
    find "$dir" -maxdepth 4 -type f \( -iname '*dpu*' -o -iname '*kv260*' -o -iname '*k26*' \) -print 2>/dev/null | head -80
  fi
done
echo

echo "[STORAGE / MEMORY]"
df -h / 2>&1 || true
free -h 2>&1 || true
echo
echo "Check complete. This inventory does not prove that a model can be compiled or run on the DPU."
