# iCAD Dispatch Template Variables (Text Expansion for Alert Messages)

This document describes the **template variables** you can use inside alert message templates (Email, Telegram, Discord, Pushover, Make.com, n8n, etc.).

These variables are used for **text expansion**: when an alert is sent, the delivery module loads a message template (subject/body/embed fields/etc.)

That function replaces placeholders like `{system_name}` or `{timestamp_local}` with real values from the **dispatch context** (`ctx`) for the specific call being sent.

---

## Placeholder reference

### Identification

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `system_id` | int | `system_row["radio_system_id"]` | Internal system ID (cast to int). |
| `system_name` | str | `system_row["system_name"]` | Human-readable system name (default empty). |

---

### Talkgroup

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `talkgroup_id` | str | `payload["talkgroup"]` | Talkgroup value, coerced to string. |
| `talkgroup_name` | str | `payload["talkgroup"]` | Same as talkgroup_id (no TG lookup table in this schema). |

---

### Incident classification (ONLY 3 fields + JSON)

These placeholders let you include the system’s **best guess about what kind of call this is** (category + specific type), plus a confidence score. They’re meant for **templates / message formatting** (Discord, Telegram, email, etc.). If incident classification isn’t available for a call, the text fields show `-` and the confidence is `0.0`.

#### How to use them

- Use **`{incident_category}`** to show the broad bucket (ex: Fire, Medical, Traffic).
- Use **`{incident_type}`** to show the specific label (ex: Structure Fire, Chest Pain, MVC (With Injuries)).
- Use **`{incident_confidence}`** if you want to display (or debug) how confident the system was.
- Use **`{incident_json}`** when you need a single “all-in-one” value (for logs, embeds, or passing to another system).

| Placeholder | Type | Meaning / Notes |
|---|---|---|
| `incident_category` | str | Broad incident category. Shows `-` when unknown/unavailable. |
| `incident_type` | str | Specific incident type within the category. Shows `-` when unknown/unavailable. |
| `incident_confidence` | float | Confidence score from `0.0` to `1.0` (higher = more confident). Defaults to `0.0` when not available. |
| `incident_json` | str (JSON) | JSON string containing all three fields: `{ "category": "...", "incident_type": "...", "confidence": 0.0 }`. Useful for embeds/logging/integrations. |

**Examples**

- `Call Type: {incident_category} / {incident_type}`
- `Classification: {incident_category} ({incident_confidence})`
- `Debug: {incident_json}`
- 
---

### Triggers

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `trigger_names` | list[str] | `_list_names(fired_trigger_data)` | List form (best for JSON). |
| `trigger_list` | str | joined names | CSV string of triggers (ex: `A, B, C`). |
| `trigger_list_lines` | str | joined names | One trigger per line (multiline). |
| `trigger_count` | int | `len(trig_names)` | Number of triggers fired. |

---

### Audio & stream

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `audio_url` | str | `payload["audio_url"]` | URL (or path) to the audio for this call. |
| `stream_url` | str | `system_row["stream_url"]` | Stream URL for the system (defaults empty). |

---

### Timing

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `duration_s` | float | `payload["duration_s"]` | Rounded to 2 decimals. |
| `duration_hms` | str | `_fmt_hms(duration_s)` | Friendly format, like `HH:MM:SS` (depends on your helper). |
| `start_epoch_s` | int | `payload["start_epoch_s"]` | Start time epoch seconds. |
| `timestamp` | int | alias | Alias of `start_epoch_s` for convenience. |
| `timestamp_12` | str | `_ts_local(...)` | 12-hour human time (exact format depends on `_ts_local`). |
| `timestamp_24` | str | `_ts_local(...)` | 24-hour human time (exact format depends on `_ts_local`). |
| `timestamp_local` | str | `_ts_local(...)` | Local time string in `tz`. |
| `timestamp_utc` | str | `_ts_local(...)` | UTC time string (typically ISO-8601). |

---

### Transcript

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `transcript` | str | `transcript_text` | Final transcript text (trimmed). |
| `transcript_text` | str | alias | Same as `transcript`. |
| `transcript_segments` | list[dict] | `transcript_segments` | Segment list (defaults empty list). |
| `transcript_segments_json` | str (JSON) | json-dumped segments | JSON string version of segments list. |

Fallback behavior:
- If `transcript_text` is None and `transcript_segments` exists, the code tries to build `transcript_text` by concatenating each segment’s `text` field (joined with spaces).

---

### Tones

| Placeholder | Type | Source | Meaning / Notes |
|---|---|---|---|
| `tones_summary` | usually str | `summarize_tones(detect_result)` | Whatever your summarize function returns (commonly a human-readable summary). |

---

### Address (unified view)

You accept two payload fields that may be dicts OR JSON strings:

- `payload["address_extracted"]` (LLM-extracted pieces)
- `payload["address_geocoded"]` (geocoder output)

Both are parsed defensively: if parsing fails, they become `{}`.

Then you produce a *unified* address view, with this priority:

1) If geocoded data exists → `address_source = GEOCODED` and unified fields come from geocoded values.
2) Else if extracted data exists → `address_source = EXTRACTED` and unified fields come from extracted values.
3) Else → `address_source = NONE` and unified fields are empty.

| Placeholder | Type | Meaning / Notes |
|---|---|---|
| `address_source` | str | One of: `GEOCODED`, `EXTRACTED`, `NONE`. |
| `address_raw` | str | “Raw” address text (prefers geocoded formatted text; may fall back to extracted raw/line). |
| `address_line` | str | Best single-line address (prefers geocoded line; may fall back to extracted). |
| `address_city` | str | City/locality (geocoded uses city/locality). |
| `address_county` | str | County. |
| `address_state` | str | State/administrative area. |
| `address_postal` | str | Postal/ZIP. |
| `address_country` | str | Country (can fall back from extracted if geocoder omitted it). |
| `address_lat` | float or null | Latitude if available (converted to float). |
| `address_lng` | float or null | Longitude if available (converted to float). |
| `address_maps_url` | str | Maps link if provided by geocoder. |
| `address` | dict | The full unified address object (not string). Useful if you render JSON. |
| `address_json` | str (JSON) | JSON string version of the unified address object. |

The unified `address_json` looks like:

```json
{
  "source": "GEOCODED",
  "line": "125 Sunset Street, Sayre, PA 18840",
  "raw": "125 Sunset Street, Sayre, PA 18840, USA",
  "city": "Sayre",
  "county": "Bradford",
  "state": "PA",
  "postal": "18840",
  "country": "US",
  "lat": 41.12345,
  "lng": -76.54321,
  "maps_url": "https://maps.google.com/?q=..."
}
```

(Example only; exact contents depend on your payload.)

---

## Example templates

### Simple alert line

```text
🚨 {system_name} / TG {talkgroup_id}
Time: {timestamp_local}
Incident: {incident_category} - {incident_type} ({incident_confidence})
Address: {address_line} ({address_source})
Audio: {audio_url}
Triggers:
{trigger_list_lines}
```

### JSON-friendly payload embed

If your destination expects JSON, these are easiest to drop in:

- `incident_json`
- `address_json`
- `transcript_segments_json`

```text
Incident JSON: {incident_json}
Address JSON: {address_json}
Segments JSON: {transcript_segments_json}
```

---
