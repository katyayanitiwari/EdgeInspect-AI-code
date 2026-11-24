# EdgeInspect-AI — KV260 first boot (Milestone K0)

This is the first hardware milestone. At this stage, we are **only bringing up Linux and recording the exact board software environment**. Do not install the laptop's full `requirements.txt`, copy model files, wire the Renesas board, or attempt FPGA acceleration yet.

## 1. Check the accessories before applying power

The KV260 starter kit itself contains the K26 SOM, carrier card, and integrated thermal solution. AMD explicitly lists the power supply and microSD card as **not included** in the KV260 box.

Required for this bring-up:

- KV260 board with the fan/heatsink fitted.
- A microSD card suitable for the AMD image (follow the current AMD guide for the supported card specification).
- A regulated **12 V, 3 A** supply with a **5.5 mm outer / 2.5 mm inner barrel connector, centre-positive** polarity. Check its printed label and polarity; do not try a random 12 V adapter.
- Ethernet cable to put the KV260 and development laptop on the same LAN.
- Optional: HDMI monitor/keyboard, or a USB-to-UART console connection for first login.

Official references:

- [AMD KV260 Getting Started / Software Getting Started](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Software-Getting-Started)
- [AMD KV260 — What's in the Box](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/What-s-in-the-Box)
- [AMD KV260 — Power requirements](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Powering-the-Starter-Kit-and-Power-Budgets)

## 2. Prepare the microSD image

1. Open AMD's current KV260 Getting Started page above.
2. Download the **KV260/Xilinx SOM Starter Linux image** linked from that guide. Do not use a KR260 image or an image intended for a different K26 carrier board.
3. Flash the image to the microSD card using the flashing method recommended by AMD (for example, a verified image writer such as balenaEtcher, if the guide directs you there).
4. Safely eject the card and insert it into the KV260 microSD slot (J11).

The board's QSPI contains its primary boot firmware; the Linux OS is booted from the microSD secondary boot device. Do not update QSPI firmware as part of this first bring-up.

## 3. First power-on

1. Keep the board on a non-conductive, ventilated surface. Do not handle exposed circuitry while powered.
2. Connect Ethernet to the same router/switch as the laptop.
3. Connect the verified 12 V supply to the KV260 DC input (J12).
4. Observe the fan and status LEDs. Give the first boot time to complete.
5. Open a Linux terminal on the board (HDMI/keyboard or serial console) and sign in using the credentials supplied by AMD for the image you downloaded. Do not assume credentials from an unrelated prebuilt image.

## 4. Collect the board report

Copy `collect_system_info.sh` to the KV260, then run:

```bash
chmod +x collect_system_info.sh
./collect_system_info.sh
cat kv260_system_report_*.txt
```

The script is read-only: it records OS, kernel, CPU architecture, Python, memory, storage, network interfaces, camera device nodes, and available AMD utilities. It does not install packages or change board settings.

Expected CPU architecture is normally `aarch64`. Record the entire report and send it back before we choose compatible PyTorch/Ultralytics/ONNX packages. Package compatibility depends on the actual Linux image, Python version, and available ARM64 wheels.

## 5. K0 acceptance checklist

K0 is complete only when all are true:

- KV260 reaches a Linux login prompt.
- The board has a LAN IP address.
- The laptop can reach the board over the LAN (or serial console is available for troubleshooting).
- `collect_system_info.sh` completes and produces a report.
- The exact OS image/release, kernel, Python version, and architecture are known.

## What happens immediately after K0

- **K1:** transfer the existing steel checkpoint and a small held-out NEU-DET test set; run the existing CPU smoke benchmark on KV260.
- **K2:** only after K1, connect the laptop webcam stream over the LAN and run inference on the KV260.
- **K3:** evaluate Vitis AI/DPU acceleration only after the CPU baseline is repeatable.
- **Renesas:** add BGK-RA6E2 after its exact UART routing/jumper configuration is checked against its manual. No pins are wired in K0.

Do not report KV260 inference, camera streaming, FPGA acceleration, or Renesas integration as completed until measured on the physical boards.
