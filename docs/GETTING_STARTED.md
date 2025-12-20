# Getting Started: Add a System & Start Receiving Audio

This guide walks you through the minimum steps to:

- Create a Radio System in the dashboard
- Enable Tone Finder (so calls with tones are saved)
- Upload dispatch audio into the app (RDIO-compatible)
- Verify tone hits are being detected

---

## 1) Create a Radio System

1. Open the dashboard and go to **Edit Systems**.
2. Click **Add System**.
3. Fill out:

- **System ID**  
  This is your public system identifier (**system_decimal**) and it **must match** what your uploader sends as `system` / `system_id` (or `X-System-ID`).  
  Example: `6643`

- **System Name**  
  Friendly label shown in the UI.  
  Example: `Ohio MARCS-IP`

- **Stream URL (optional)**  
  A URL where a user can listen to the system (Icecast, Broadcastify, etc.). This is optional and does not affect uploading.

4. Click **Save**.

✅ At this point the system exists, but it won’t store anything unless Tone Finder is enabled or a Trigger fires.

---

## 2) Get the system API token

The `api/call-upload` endpoint requires a **system-scoped API key**.

Uploads must include:

- a valid API token (`Authorization: Bearer <token>` or `key=<token>`)
- a matching **System ID** (system_decimal) via `system=<id>` / `system_id=<id>` or header `X-System-ID: <id>`

If either is missing or wrong, your API returns JSON errors like:

- `missing_token` (401)
- `missing_system_id` (400)
- `system_not_found` (404)
- `invalid_token` (403)

**Rule:** the token must be the exact value stored in `radio_systems.api_key` for that system.

---

## 3) Enable Tone Finder (minimum required to save calls)

Tone detection runs on every upload, but calls are only persisted when:

- **Tone Finder is enabled** *and* tones are detected, **or**
- a **Trigger fires**.

To “just start seeing activity”:

1. Select your new system from the **Systems** dropdown.
2. Go to **Tone Settings**
3. Turn on:
   - ✅ **Tone Finder Enabled**

Now any upload containing tones will be stored and show up in **Tone Hits**.

---

## 4) Upload audio into iCAD Dispatch

Your upload endpoint is **RDIO compatible**, meaning it accepts the same general multipart form format RDIO expects.

### Endpoint
`POST api/call-upload`

### Required field
- `audio` = file (multipart upload)

### Required auth + system identification
Choose **one token method** + **one system id method**:

**Token**
- `Authorization: Bearer <api_key>` **(recommended)**
- or `key=<api_key>` (form/query)

**System ID**
- `system=<system_decimal>` or `system_id=<system_decimal>` (form/query)
- or header `X-System-ID: <system_decimal>`

### Recommended fields (RDIO-style)
These aren’t strictly required, but they improve timing/metadata:

- `talkgroup` (example: `12345`)
- `start_time` (epoch seconds) **or** `dateTime` (ISO UTC)

If neither `start_time` nor `dateTime` is provided, iCAD will default to “now”.

---

## 5) Upload options (3 common ways)

### Option A — RDIO Downstream (recommended)
If you already have RDIO Scanner running upstream, use **RDIO Scanner Downstream** to forward dispatch channel audio to iCAD Dispatch.

**Key point:** the System ID in the downstream config must match the **System ID** you created in the UI (system_decimal).

### Option B — A simple upload script
Use your included `upload_example.py` as a reference. This is great for:

- testing
- replaying sample audio
- uploading from a cron job or glue service

### Option C — Scanner software plugin (SDRTrunk / Trunk Recorder / VoxCall / etc.)
Many scanner pipelines already have an “RDIO-like” uploader or plugin model.

Configure the plugin/uploader to send:

- system id = your iCAD **System ID**
- token = your iCAD system **API key**
- url = the url to iCAD Dispatch (some require path /api/upload-call)

---

## 6) Verify audio is flowing

### Quick success signals
When things are working you’ll see:

- HTTP **201** response from `api/call-upload` for normal imports
- HTTP **202** when a “tone-only stub” is stored (split mode) and it’s waiting for voice
- entries appearing in **Tone Finder → Tone Hits** (when Tone Finder is enabled and tones are present)

### What the responses mean
- **201 Created**: the call was imported (and possibly stored + triggers processed)
- **202 Accepted**: split mode cached a “stub” (tone-only) and will merge when a matching voice clip arrives
- **4xx JSON error**: auth/system mismatch or bad input
- **422**: audio validation failed

---

## 7) Next steps (after you see tone hits)

Once audio is coming in:

1. **Add Triggers** for your system (so alerts fire when tones match).
2. Configure per-system destinations:
   - File Storage
   - Discord fields
   - Telegram
   - Pushover
   - Email
   - Make webhooks
3. Optional: enable transcription, address extraction, incident classification.

---

## Troubleshooting

### “System not found” (404)
Cause: the uploader is sending a `system` / `system_id` / `X-System-ID` value that doesn’t exist in your UI.

Fix: make sure the uploader’s system id equals the **System ID** you created (system_decimal).

### “Invalid token for this system” (403)
Cause: the token is valid *for some system*, but not for this system id.

Fix: verify you’re using the matching `radio_systems.api_key` for that system.

### Upload succeeds but nothing shows up in Tone Hits
Usually means:
- Tone Finder is disabled, and
- no triggers fired, or
- the audio didn’t contain detectable tones.

Fix: enable Tone Finder for that system first.

---

## Copy/paste examples

### Example: curl upload (multipart)
^^^bash
curl -X POST "https://YOUR_HOST/call-upload" \
  -H "Authorization: Bearer YOUR_SYSTEM_API_KEY" \
  -F "system=6643" \
  -F "talkgroup=12345" \
  -F "start_time=1765987420" \
  -F "audio=@dispatch.mp3"
^^^

### Example: success response (201)
^^^json
{
  "success": true,
  "message": "Call imported successfully",
  "result": {
    "radio_system_id": 12,
    "merged": false,
    "triggers_fired": [],
    "audio_url": "https://YOUR_HOST/static/audio/12_12345_1765987420.mp3"
  }
}
^^^

### Example: stub stored (202)
^^^json
{
  "success": true,
  "message": "Tone-only stub stored; waiting for voice.",
  "result": {
    "radio_system_id": 12,
    "stub": true
  }
}
^^^

### Example: auth/system error (JSON)
^^^json
{
  "success": false,
  "error": {
    "status": 403,
    "message": "Invalid token for this system.",
    "code": "invalid_token",
    "system_decimal": 6643
  }
}
^^^
