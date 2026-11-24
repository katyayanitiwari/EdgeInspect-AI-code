# KV260 ↔ RA6E2 UART message contract

This is an application protocol proposal for the current prototype; it is not a Renesas or AMD standard. It lets the KV260 send a small inspection summary to the RA6E2. Images and model inference remain on KV260.

## Electrical / board setup

- First confirm the exact Renesas board: FPB-RA6E2, EK-RA6E2, or another board. Connector routing and pins are board-specific.
- Configure an SCI UART in Renesas FSP/e² studio as 115200 baud, 8 data bits, no parity, 1 stop bit (8-N-1), with receive interrupts enabled. Choose pins only after checking the exact board manual and jumper configuration.
- Use a compatible 3.3 V UART logic interface and shared ground for a direct UART connection. Never connect a 5 V UART TX directly to RA6E2 GPIO.
- The KV260 Linux UART device or USB-to-UART adapter must be identified on the actual setup; do not assume a device path.

## Line format, version 1

ASCII fields separated by `|`, terminated by LF (`\n`), with a maximum complete line length of 96 bytes. CR before LF may be ignored.

KV260 result to RA6E2:

```text
EI1|RESULT|<id>|<mode>|<decision>|<severity>|<count>\n
```

Example:

```text
EI1|RESULT|42|steel|REJECT|critical|2
```

Allowed values:

- `id`: decimal integer 1–2147483647; unique while a command is outstanding.
- `mode`: `steel` or `pcb`. PCB mode must not be used until a PCB model is trained and validated.
- `decision`: `PASS`, `REJECT`, or `MANUAL_REVIEW`.
- `severity`: `none`, `minor`, `major`, or `critical`.
- `count`: decimal integer 0–99.

RA6E2 acknowledgement:

```text
EI1|ACK|42|OK\n
```

Malformed/unsupported input:

```text
EI1|NACK|42|INVALID\n
```

When the frame header and inspection ID can be parsed, the RA6E2 should echo that ID in its NACK. For a malformed frame where no valid ID can be recovered, the current firmware template uses `0` as an "unknown request ID" sentinel; the KV260 sender treats that as an invalid/unmatched reply. Normal request IDs remain 1–2147483647.

An operator trigger may be sent RA6E2 to KV260 as `EI1|TRIGGER|43|INSPECT\n`; the KV260 should respond with `EI1|ACK|43|OK\n` once it has accepted the trigger. A trigger requests inspection; it does not claim the inspection succeeded.

## Behavior and safety

- Receive one line at a time. Reject overlong, malformed, unsupported-version, and out-of-range fields. Never buffer without a fixed size.
- ACK only after a valid message has been parsed. Repeated IDs should be handled idempotently to avoid duplicate alerts.
- On boot, timeout, malformed input, or communication loss, set the indicator state to a neutral/manual-review state. Do not activate an actuator based only on model output.
- Initially use only onboard LEDs for `PASS`, `REJECT`, and `MANUAL_REVIEW`; buzzer/relay/motor wiring requires a suitable driver and separate bench validation.
- UART is not authenticated. Keep it on a direct cable or trusted local link; do not expose a serial-to-network bridge publicly.

## Status

The message contract and software examples are prepared in the repository. UART pin routing, the correct serial device, FSP build, flashing, and end-to-end behavior require the physical boards and remain unverified.
