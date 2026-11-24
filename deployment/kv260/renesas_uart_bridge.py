"""Send one inspection summary from KV260 Linux to a Renesas RA6E2 UART.

The board pins and serial device name are intentionally supplied at run time;
they depend on the actual KV260 image, UART adapter, RA6E2 board and FSP setup.
"""
from __future__ import annotations

import argparse
import sys
import time

MAX_LINE_BYTES = 96
VALID_MODES = {"steel", "pcb"}
VALID_DECISIONS = {"PASS", "REJECT", "MANUAL_REVIEW"}
VALID_SEVERITIES = {"none", "minor", "major", "critical"}


def make_result_line(inspection_id: int, mode: str, decision: str,
                     severity: str, defect_count: int) -> bytes:
    """Validate and encode a version-1 result line, including its LF terminator."""
    if not 1 <= inspection_id <= 2_147_483_647:
        raise ValueError("inspection_id must be from 1 to 2147483647")
    if mode not in VALID_MODES:
        raise ValueError("mode must be 'steel' or 'pcb'")
    if decision not in VALID_DECISIONS:
        raise ValueError("decision must be PASS, REJECT, or MANUAL_REVIEW")
    if severity not in VALID_SEVERITIES:
        raise ValueError("severity must be none, minor, major, or critical")
    if not 0 <= defect_count <= 99:
        raise ValueError("defect_count must be from 0 to 99")
    line = (f"EI1|RESULT|{inspection_id}|{mode}|{decision}|{severity}|{defect_count}\n")
    encoded = line.encode("ascii")
    if len(encoded) > MAX_LINE_BYTES:
        raise ValueError("encoded message exceeds protocol line limit")
    return encoded


def wait_for_reply(port, inspection_id: int, timeout_s: float) -> str:
    """Read one bounded reply and require an ACK or report the NACK."""
    deadline = time.monotonic() + timeout_s
    line = bytearray()
    while time.monotonic() < deadline:
        chunk = port.read(1)
        if not chunk:
            continue
        if chunk == b"\n":
            reply = line.decode("ascii", errors="strict").rstrip("\r")
            fields = reply.split("|")
            if len(fields) == 4 and fields[0] == "EI1" and fields[2] == str(inspection_id):
                if fields[1] == "ACK" and fields[3] == "OK":
                    return reply
                if fields[1] == "NACK":
                    raise RuntimeError(f"RA6E2 rejected the message: {fields[3]}")
            raise RuntimeError(f"unexpected RA6E2 reply: {reply!r}")
        line.extend(chunk)
        if len(line) >= MAX_LINE_BYTES:
            raise RuntimeError("RA6E2 reply exceeded protocol line limit")
    raise TimeoutError(f"no matching ACK received within {timeout_s:g} seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Linux serial device path, determined on the board")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--id", type=int, default=1, dest="inspection_id")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="steel")
    parser.add_argument("--decision", choices=sorted(VALID_DECISIONS), required=True)
    parser.add_argument("--severity", choices=sorted(VALID_SEVERITIES), required=True)
    parser.add_argument("--defect-count", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=2.0, help="ACK timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print the message without opening UART")
    args = parser.parse_args()

    try:
        message = make_result_line(args.inspection_id, args.mode, args.decision,
                                   args.severity, args.defect_count)
        if args.baud <= 0 or args.timeout <= 0:
            raise ValueError("baud and timeout must be positive")
        if args.dry_run:
            sys.stdout.write(message.decode("ascii"))
            return 0
        if not args.port:
            parser.error("--port is required unless --dry-run is used")
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required; install it in the KV260 environment first") from exc

        with serial.Serial(args.port, args.baud, timeout=0.1, write_timeout=1.0,
                           bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE) as port:
            port.reset_input_buffer()
            port.write(message)
            port.flush()
            print(f"Sent {message.decode('ascii').rstrip()}")
            print(f"Received {wait_for_reply(port, args.inspection_id, args.timeout)}")
        return 0
    except (ValueError, RuntimeError, TimeoutError, UnicodeDecodeError, OSError) as exc:
        print(f"UART bridge error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
