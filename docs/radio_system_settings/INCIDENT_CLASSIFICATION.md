# Incident Classification

Incident Classification uses an OpenAI model to label each dispatch transcript with:

- a **category** (ex: Fire, Medical, Traffic)
- a **specific incident type** (ex: Structure Fire, Chest Pain, MVC (With Injuries))
- a **confidence score** (0.0–1.0)

These labels are then attached to the call payload so they can be used by:
- your dashboards (filters, badges, sorting)
- your alert routing rules (ex: only Fire/Medical triggers)
- your text expansion placeholders (ex: `{incident_category}`, `{incident_type}`, `{incident_confidence}`, `{incident_json}`)

---

## What it classifies

Incident Classification is designed for **fire/EMS-style dispatch transcripts** where the system should pick the **primary incident** being dispatched.

It intentionally ignores “radio noise” like:
- repeated dispatch lines
- unit acknowledgements
- timestamps / scanner artifacts

The model must choose exactly **one** `(category, incident_type)` pair from your allowed taxonomy.

---

## Requirements

To enable Incident Classification for a radio system, you need:
1. **Transcribe Enabled** for that system
2. **Incident Classification enabled** for that system
3. A valid **OpenAI API key** available either:
   - stored in the system’s Incident Classification settings, **or**
   - provided via the server environment variable `OPENAI_API_KEY`
4. A selected **OpenAI model** (example: `gpt-4o-mini`)

If classification is enabled but the key/model is missing, classification will not run.

---

## Configuration in the UI

Go to the radio system editor and open the **Incident Classification** tab.

### 1) Enable / Disable
- **Incident Classification:** `Enabled` or `Disabled`

When disabled, no classification runs and no incident labels are produced.

### 2) OpenAI API Key
- **OpenAI API Key:** used to classify incidents from transcripts
- This can be left blank if your server already provides `OPENAI_API_KEY`

Tip: If you run multiple systems and want them all to share one key, using `OPENAI_API_KEY` at the server level is usually easiest.

### 3) Model
Choose one of the allowed models:
- `gpt-4o-mini` (recommended default)
- `gpt-4o`
- `gpt-4.1-mini` (untested)
- `gpt-4.1`      (untested)

### 4) Min confidence (0..1)
This is a quality gate.

- `0.0` = accept all classifications (even low-confidence ones)
- `0.6` = only keep classifications when the model is fairly sure
- `0.8` = only keep very confident classifications

If a result is below the threshold, it is treated as “no classification” for that call.

Recommended starting point:
- **0.0** while testing/tuning
- then **0.5–0.7** once you’re happy with accuracy

### 5) Save
Click **Save Incident Settings** to store the configuration.

## What you get when it runs

When classification succeeds, the call will have incident data available for:

- UI display (badges, labels)
- filtering/searching
- downstream alert formatting via text expansion placeholders:
  - `{incident_category}`
  - `{incident_type}`
  - `{incident_confidence}`
  - `{incident_json}`

When classification does **not** run (disabled, missing key, below min confidence, or an error), those placeholders fall back to:
- category/type: `-`
- confidence: `0.0`

---

## Practical examples

### Use in an alert message
**Discord / Telegram message template**
- `🚨 {incident_category}: {incident_type} ({incident_confidence})`

### Use for debugging
- `Incident JSON: {incident_json}`

### Use for routing / filtering
Common patterns:
- prioritize **Fire + Medical**
- de-prioritize **Other**
- special handling for **MVC (With Injuries)** vs **MVC (Unknown Injuries)**

---

## Troubleshooting

### “It’s enabled but nothing is showing”
Check:
- the system is set to **Enabled**
- you have a valid key configured (or `OPENAI_API_KEY` is set on the server)
- the model is selected
- `min_confidence` isn’t set too high (try `0.0` temporarily)

### “Confidence is always 0.0”
That typically means classification did not run or the result was rejected by the confidence threshold.

### “I only want classification sometimes”
That’s exactly what per-system enable + `min_confidence` is for:
- disable for noisy systems
- raise threshold for systems with messy transcripts
- lower threshold for systems with short, clean dispatch text
