#!/usr/bin/env python3
"""
Example uploader for POST /api/call-upload

Sends multipart/form-data:
  - audio: file (required)
  - plus optional form fields: talkgroup, start_time, dateTime, etc.

Auth:
  - Authorization: Bearer <token>
  - X-API-Key: <token>
  - form field key=<token>  (your route already skips "key" when building call_data)

Usage examples:
  python upload_call_example.py \
    --url "https://example.com/api/call-upload" \
    --token "$ICAD_API_KEY" \
    --audio ./clip.mp3 \
    --talkgroup 1234 \
    --start-time "$(date +%s)"

  # Or use ISO-8601 instead of start_time:
  python upload_call_example.py --url http://localhost:9911/api/call-upload \
    --token "$ICAD_API_KEY" --audio ./clip.wav \
    --talkgroup 1234 \
    --date-time "2025-12-18T20:15:10Z"

  # Add arbitrary extra fields (repeated):
  python upload_call_example.py --url http://localhost:9911/api/call-upload \
    --token "$ICAD_API_KEY" --audio ./clip.mp3 \
    --field "freq=851.0125" --field "src=trunk-recorder" --field "unit=E1"
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
from typing import Dict, Tuple, Optional

import requests


def guess_mimetype(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def parse_kv(s: str) -> Tuple[str, str]:
    if "=" not in s:
        raise argparse.ArgumentTypeError("Expected KEY=VALUE")
    k, v = s.split("=", 1)
    k = k.strip()
    if not k:
        raise argparse.ArgumentTypeError("KEY cannot be empty")
    return k, v


def main() -> int:
    ap = argparse.ArgumentParser(description="Example uploader for /api/call-upload")
    ap.add_argument("--url", required=True, help="Full endpoint URL, e.g. http://localhost:9911/api/call-upload")
    ap.add_argument("--audio", required=True, help="Path to audio file (mp3/wav/etc)")
    ap.add_argument("--token", default=os.getenv("ICAD_API_KEY", ""), help="API token/key (or set ICAD_API_KEY env var)")
    ap.add_argument("--no-form-key", action="store_true", help="Do NOT include form field key=<token>")
    ap.add_argument("--talkgroup", default=None, help="Talkgroup (string or int)")
    ap.add_argument("--start-time", default=None, help="Epoch seconds (int/float). If omitted, will use now().")
    ap.add_argument("--date-time", default=None, help="ISO-8601 UTC timestamp (e.g. 2025-12-18T20:15:10Z)")
    ap.add_argument("--timeout", type=float, default=120.0, help="HTTP timeout seconds")
    ap.add_argument("--field", action="append", default=[], type=parse_kv, help="Extra form field KEY=VALUE (repeatable)")
    ap.add_argument("--verbose", action="store_true", help="Print request/response details")

    args = ap.parse_args()

    if not os.path.exists(args.audio):
        print(f"ERROR: audio file not found: {args.audio}", file=sys.stderr)
        return 2

    token = (args.token or "").strip()
    if not token:
        print("ERROR: missing --token (or ICAD_API_KEY env var).", file=sys.stderr)
        return 2

    # ----------------------------
    # Build multipart form
    # ----------------------------
    data: Dict[str, str] = {}

    if args.talkgroup is not None:
        data["talkgroup"] = str(args.talkgroup)

    # Your server prioritizes start_time, then dateTime, then now().
    if args.start_time is not None:
        data["start_time"] = str(args.start_time)
    elif args.date_time is not None:
        data["dateTime"] = str(args.date_time)
    else:
        data["start_time"] = str(time.time())

    for k, v in args.field:
        # Allow user-defined fields to override defaults if they really want
        data[k] = v

    if not args.no_form_key:
        data["key"] = token  # server skips this from call_data anyway

    headers = {
        # Include both common header styles to match your decorator implementation
        "Authorization": f"Bearer {token}",
        "X-API-Key": token,
    }

    mime = guess_mimetype(args.audio)
    filename = os.path.basename(args.audio)

    if args.verbose:
        safe_headers = dict(headers)
        safe_headers["Authorization"] = "Bearer ***"
        safe_headers["X-API-Key"] = "***"
        safe_data = dict(data)
        if "key" in safe_data:
            safe_data["key"] = "***"
        print("POST", args.url)
        print("headers:", safe_headers)
        print("data:", safe_data)
        print("file:", {"audio": (filename, mime)})

    with open(args.audio, "rb") as f:
        files = {
            "audio": (filename, f, mime),
        }
        try:
            r = requests.post(
                args.url,
                headers=headers,
                data=data,
                files=files,
                timeout=args.timeout,
            )
        except requests.RequestException as e:
            print(f"ERROR: request failed: {e}", file=sys.stderr)
            return 3

    # ----------------------------
    # Print response
    # ----------------------------
    print(f"HTTP {r.status_code}")
    ct = (r.headers.get("content-type") or "").lower()

    if "application/json" in ct:
        try:
            payload = r.json()
        except Exception:
            payload = None

        if payload is not None:
            print(json.dumps(payload, indent=2, sort_keys=False))
        else:
            print(r.text)
    else:
        print(r.text)

    # Non-2xx still returns useful JSON in your route
    return 0 if 200 <= r.status_code < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
