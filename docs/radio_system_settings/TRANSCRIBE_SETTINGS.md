# Transcribe Settings (OpenAI-Compatible Speech-to-Text)

The **Transcribe** tab controls how your system generates **text transcripts** from uploaded audio by calling an *
*OpenAI-compatible transcription service** (e.g., OpenAI’s official API, or a self-hosted “OpenAI-compatible” endpoint).

When enabled, the app will send audio to your configured service and store the returned transcript for display,
searching, downstream processing, and alerting workflows.

---

## What “OpenAI-compatible” means

“OpenAI-compatible” means your transcription provider exposes an API that **looks like OpenAI’s** (same general
request/response shape), so the app can talk to it the same way whether you use OpenAI’s hosted service or a self-hosted
server on your own hardware.

---

### Hosted by OpenAI (cloud)

**OpenAI Official**

- OpenAI API: https://openai.com/api/

---

### Hosted locally (self-hosted)

**Self-hosted OpenAI-compatible services**

- iCAD Transcribe: https://github.com/TheGreatCodeholio/icad_transcribe
- Speaches: https://github.com/speaches-ai/speaches

---

## Settings

### 1) Transcribe (Enabled / Disabled)

**What it does:** Turns transcription on or off for this radio system.

- **Enabled (1):** Audio uploads will be transcribed (when applicable).
- **Disabled (0):** No transcription calls are made; transcripts remain empty.

---

### 2) Transcribe URL

**What it does:** Sets the **base URL** for your transcription service.

- **Important:** You **do not** need to include an endpoint path here (no `/v1/...`). The app expects a base URL and
  will call the OpenAI-style route on that host.
- **Leave blank for OpenAI Official:** If empty, the app will use OpenAI’s official API base (and call
  `https://api.openai.com/v1/audio/transcriptions`).

**Examples:**

- OpenAI official base: *(leave empty)*
- Self-hosted service base: `https://transcribe.yourdomain.com`
- Local/LAN service base: `http://192.168.1.50:8000`

**Common mistake:** Putting the full path in this field (like `https://host/v1/audio/transcriptions`) can lead to
double-path issues (404s).

---

### 3) Transcribe API Key

**What it does:** The token used to authenticate with your transcription service.

- For **OpenAI official**, this should be your OpenAI API key.
- For **self-hosted**, use whatever token your service expects.

---

### 4) Model

**What it does:** Selects the speech-to-text model ID sent to the service.

**Can be left empty, this uses the default OpenAi Whisper model or default Runtime on iCAD Transcribe**

---

### 5) Language

**What it does:** Hints the language of the audio to improve accuracy and reduce latency.

- Use an **ISO-639-1** code such as `en` (or whatever your backend accepts).
- If left blank, many services attempt auto-detection (behavior depends on the backend).

OpenAI notes that supplying the language can improve accuracy and latency.

**Examples:**

- `en` (English)
- `es` (Spanish)
- `fr` (French)

---

### 6) Prompt / Hints

**What it does:** Provides optional context to bias recognition (names, jargon, radio phrases, unit IDs, geography).

OpenAI describes this as “optional text to guide the model’s style or continue a previous audio segment,” and notes it
should match the audio language.

**Warning**
This can cause text to be added that is NOT part of the transcript sometimes.

---
