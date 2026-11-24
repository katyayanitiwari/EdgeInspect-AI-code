# Renesas RA6E2 support-controller track

The RA6E2 is a microcontroller, not the primary vision processor. In EdgeInspect-AI it can act as an inspection I/O controller for status LEDs, buzzer, inspection trigger, and a future reject actuator. The vision model and Llama runtime remain on the KV260 Arm Linux side.

## Board variant must be confirmed

Renesas has two distinct RA6E2 development boards:

- EK-RA6E2: https://www.renesas.com/en/design-resources/boards-kits/ek-ra6e2
- FPB-RA6E2: https://www.renesas.com/en/design-resources/boards-kits/fpb-ra6e2

Their connectors, pin routing, and available Pmod/UART routing differ. This package deliberately does not assign MCU pins until the exact board variant and jumper settings are confirmed.

## Proposed line protocol

Use the bounded ASCII line protocol in [`protocol.md`](protocol.md), with the UART starting point 115200 baud, 8-N-1. The KV260-side sender is `../kv260/renesas_uart_bridge.py`; the Renesas FSP integration example is under `ra6e2_fsp/`. Neither has been exercised on physical boards yet.

## Safety and electrical rules

- Confirm signal voltage and pin mapping from the specific board manual before wiring. Do not connect 5 V UART signals directly to 3.3 V MCU pins.
- Connect signal ground between boards when using non-isolated UART.
- Cross TX to RX and RX to TX; do not connect two TX pins together.
- Verify UART peripheral channel, pins, and board jumpers in Renesas FSP/e² studio for the actual board.
- Drive buzzers, relays, lamps, or motors through suitable transistor/driver stages; do not power loads directly from an MCU GPIO.
- Keep the default on reset/fault as `MANUAL_REVIEW` / no actuator action. A software defect prediction should not directly actuate safety-critical machinery in this prototype.

## Firmware milestones

1. Create the board project in Renesas e² studio / FSP for the exact board.
2. Configure a UART channel after checking the board manual and available pins.
3. Echo a newline-terminated test message over UART.
4. Add a bounded line buffer and parser following `protocol.md`.
5. Validate protocol version, fields, and inspection ID; ACK valid accepted messages.
6. Map `PASS`, `REJECT`, and `MANUAL_REVIEW` to the on-board LEDs/buzzer only after bench testing.
7. Add timeout, malformed-message, and reset tests.

## e² studio/FSP project setup (Windows)

Do this after confirming which board is on your desk:

1. Install the Renesas e² studio release and RA FSP version listed for that exact board on Renesas' official board page.
2. Create a new RA6E2 project using the exact board or MCU. The FPB-RA6E2 product page specifies `R7FA6E2BB3CFM`; confirm the EK board's exact device from its manual.
3. In the FSP Configuration editor, add **Connectivity → UART (r_sci_uart)**. Start with 115200 baud, 8 data bits, no parity, 1 stop bit; set its callback name to `edgeinspect_uart_callback` and use receive interrupts.
4. Select UART peripheral pins only after checking the chosen board's connector, jumpers/option links, and manual. Build a loopback/terminal echo first.
5. Integrate `ra6e2_fsp/edgeinspect_uart_app.c` as the project `hal_entry.c` implementation while retaining generated `hal_data.h`. Map `indicate_manual_review()` and `indicate_decision()` only to verified onboard LEDs.
6. Build and flash using the onboard debugger. First test with a USB-UART adapter/terminal; only then connect KV260 TX/RX/GND and run the KV260 sender.

The source example is not a generated e² studio project and has not been compiled against a board-specific FSP configuration. The `g_uart0` instance name, callback registration, board LED names, and pin assignment must match the generated project.

The protocol parser now accepts decimal digits only for numeric fields (no whitespace or sign characters), and preserves a valid inspection ID so field-validation failures can be returned as a correlated NACK. This is a source-level preparation only; compilation and UART behavior still need the exact RA6E2 project and physical board.

Do not use this MCU as a detector for camera images; its SRAM is 40 KB on the RA6E2 device, so it is reserved for low-bandwidth control messages.

## Status at project handoff

The UART message format, KV260 Linux sender, and FSP source template have been added. No RA6E2 e² studio project has been built or flashed, and no board-to-board message has been measured. Before wiring or compiling, identify the exact board (for example, FPB-RA6E2 or EK-RA6E2), its revision, and the selected UART connector/pins. See [Renesas FPB-RA6E2 official product page](https://www.renesas.com/en/design-resources/boards-kits/fpb-ra6e2), [user manual](https://www.renesas.com/en/document/mat/fpb-ra6e2-v1-users-manual), and [FSP SCI UART documentation](https://renesas.github.io/fsp/group___s_c_i___u_a_r_t.html).
