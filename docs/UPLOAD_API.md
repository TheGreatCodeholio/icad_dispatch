# UPLOAD_API

The Upload API is the **ingest endpoint** used by recorders/uploader clients to submit an audio clip to iCAD Dispatch.

It accepts an audio file plus a system identifier + token, and returns a JSON response indicating whether the call was
imported (and whether it was merged).

> Features like **Split Uploads**, **Tone Detection**, **Triggers**, **Transcription**, **Address Extraction**, and *
*Incident Classification** are implemented behind this endpoint, but each has its own dedicated documentation file.

---

## Endpoint

**Method:** `POST`  
**Content-Type:** `multipart/form-data`  
**Path:** depends on how the `api_call_upload` blueprint is registered in your app (commonly something like
`/api/call-upload` or `/api/call_upload`).

---

## Authentication & System Scope

This endpoint is system-scoped: every request must include:

### 1) API token (required)

Accepted sources:

- `Authorization: Bearer <token>`
- form/query field: `key=<token>`

### 2) System identifier (required)

System ID:
Unique id for a system to identify it. Like RDIO System ID

Accepted sources:

- form/query field: `system=<System ID>`
- form/query field: `system_id=<System ID>`
- header: `X-System-ID: <System ID>`

---

## Request fields

### Required

- `audio` (file)
    - The uploaded audio clip. Must be sent as a multipart file field named **audio**.

### Common optional fields

- `talkgroup`
    - Used for routing logic and matching triggers (if configured).
- `start_time`
    - Epoch seconds (int/float). If present, this becomes the call start time.
- `dateTime`
    - ISO-8601 UTC timestamp (Zulu or `+00:00`) used when `start_time` is not provided.

> Any additional form/query fields (other than `key`, `system`, `system_id`, and `audio`) are collected into `call_data`
> on the server and may be used by downstream logic.

---

## Timestamp rules

The server computes a call start timestamp in this order:

1. `start_time` (epoch seconds)
2. `dateTime` (ISO-8601 UTC)
3. server `time.time()` (now)

---

## Responses

### 201 Created (imported)

Returned when the upload was processed and the call was imported.

Response shape:

```json
{
  "success": true,
  "message": "Call imported successfully",
  "result": {
    "radio_system_id": 12,
    "merged": false,
    "triggers_fired": [
      "My Trigger Name"
    ],
    "audio_url": "https://example.com/static/audio/12_2978_1765987420.mp3"
  }
}
```

Notes:

- `merged` indicates whether the call was merged from a prior stub (Split Uploads behavior).
- `triggers_fired` is a list of trigger names that fired for this upload.
- `audio_url` is the final URL to the stored audio (if persisted).

### 202 Accepted (stub cached)

Returned when Split Uploads logic cached the clip as a “stub” and is waiting for a follow-up clip.

```json
{
  "success": true,
  "message": "Tone-only stub stored; waiting for voice.",
  "result": {
    "radio_system_id": 12,
    "stub": true
  }
}
```

### Error responses

There are two JSON error shapes you may see:

#### A) Auth/system-scope errors (from `token_required`)

```json
{
  "success": false,
  "error": {
    "status": 401,
    "message": "Missing API token (Authorization header or key field).",
    "code": "missing_token",
    "hint": "Send Authorization: Bearer <token> or form field key=<token>."
  }
}
```

Common auth/status codes:

- `400` missing/invalid system id
- `401` missing token
- `403` invalid token for this system
- `404` system not found
- `500` database error

#### B) Validation/processing errors (from `_err(...)`)

```json
{
  "success": false,
  "message": "audio field (file) is required",
  "result": []
}
```

Examples:

- `400` missing audio
- `422` audio validation failed
- `500` tone detection or storage failures (unexpected)

Client guidance:

- treat any non-2xx as an error
- if `error` exists, read `error.status/error.code/error.message`
- otherwise read `message`

---

## Examples

### Example 1: Authorization header + X-System-ID header

```bash
curl -X POST "https://example.com/api/call-upload" \
-H "Authorization: Bearer $API_TOKEN" \
-H "X-System-ID: 1765987420" \
-F "audio=@/path/to/clip.mp3" \
-F "talkgroup=2978" \
-F "start_time=1765987420"
```

### Example 2: key + system in form fields

```bash
curl -X POST "https://example.com/api/call-upload" \
-F "key=$API_TOKEN" \
-F "system=1765987420" \
-F "audio=@/path/to/clip.wav" \
-F "talkgroup=2978"
```

### Example 3: ISO start time (dateTime)

```bash
curl -X POST "https://example.com/api/call-upload" \
-H "Authorization: Bearer $API_TOKEN" \
-F "system=1765987420" \
-F "audio=@/path/to/clip.m4a" \
-F "dateTime=2025-12-17T16:04:38Z" \
-F "talkgroup=2978"
```

---

## Related docs

- `SPLIT_UPLOADS.md` (stub/merge behavior and tuning)
- `TONE_DETECTION.md` (what tones are detected and how they’re stored)
- `TRIGGERS.md` (how triggers match tone sets and dispatch)
- `TRANSCRIPTION.md` (transcribe settings and payload fields)
- `ADDRESS_EXTRACTION.md`
- `INCIDENT_CLASSIFICATION.md`
