# Upload Settings

These settings control two things:

- **Audio validation**: what uploads are accepted or rejected
- **Split Dispatch**: how the system combines “tones first, voice later” into one call

---

## Why these settings exist

Some radio systems commonly produce two separate uploads for a single dispatch:

1) A short clip containing **paging tones**
2) A second clip containing the **voice message**, arriving shortly after

If you treat those as two separate calls, you often end up with:

- a “call” that is mostly tones (not helpful), and
- a second “call” that is voice but missing the full context

**Split Dispatch** is designed to reduce that clutter by temporarily holding tones-only uploads and merging them into the next matching voice clip.

---

## How Split Dispatch works

When **Split Dispatch** is turned **ON**, the system evaluates each upload like this:

1) If the upload looks like **tones with not enough voice**, it is held briefly as a **pending tones clip**.
2) When the next upload for the same talkgroup arrives:
    - If it contains meaningful voice and arrives within the merge window, the system **merges the audio** and creates **one** call.
    - If it arrives too late (or never arrives), the pending tones clip is not merged.

Result: fewer “tones-only” calls, and more complete single-call audio.

> Note  
> Split Dispatch only helps when tones and voice typically arrive in separate uploads. If your tones and voice are already in the same clip, it may not be needed.

---

## Settings explained

### 1) Split Dispatch

**What it does**  
Turns the “hold tones-only clips and merge into the next voice clip” behavior on or off.

- **OFF**: Every upload becomes its own call.
- **ON**: Tones-only uploads may be held briefly and merged into the next voice clip.

**Use ON when**
- You regularly see a short tones clip followed by a separate voice clip.

**Use OFF when**
- Most uploads already include both tones and voice, or
- Your talkgroups are very busy and you want to avoid accidental merges.

---

### 2) Required voice after tones (seconds)

(Required Tail Length)

**What it does**  
Controls how strict the system is when deciding whether an upload is “tones-only” versus “contains the actual voice message.”

Think of it as:

- “After the tones end, how much real voice should be present before we treat this upload as a complete dispatch?”

**How it behaves**
- **Lower value**: the system accepts smaller amounts of voice as “good enough”  
  → fewer pending tones clips, fewer merges
- **Higher value**: the system requires more voice before it stops holding the clip  
  → more pending tones clips, more merges

**When to increase it**
- You often see tones plus a short key-up or a brief word, and then the real voice dispatch comes in the next clip.

**When to decrease it**
- Your tones clip usually already includes the full voice dispatch.

**Good starting range**
- Many setups do well around **2–3 seconds**.

---

### 3) Merge window (seconds)

(Max age between clips)

**What it does**  
Controls how long the system will wait for the “next clip” before it stops trying to merge.

Think of it as:

- “If the voice clip does not arrive within this many seconds, don’t merge.”

**How it behaves**
- **Too low**: voice arrives slightly late and you miss merges (tones-only calls slip through)
- **Too high**: you increase the chance of merging unrelated clips on busy talkgroups

**Good starting range**
- Many paging workflows do well around **20–45 seconds**.
- If your system often delays voice longer, increase it.

---

## Advanced or reserved settings

Depending on your UI, you may see additional fields. If they are visible, treat them as advanced controls.

### VAD speech ratio (0–1)

**What it is intended to control**  
A sensitivity control for how “speech-like” the audio must be.

**If your current version does not apply it**  
Changing this value may not affect results until the feature is enabled in your build.

**Recommended approach**
- Leave at the default unless you have a specific reason to tune speech sensitivity.

---

## Recommended presets

### A) Typical paging workflow (tones first, voice shortly after)

```
Split Dispatch: ON
Required voice after tones: 3 seconds
Merge window: 30 seconds
```

### B) Most uploads already include tones + full voice

```
Split Dispatch: OFF
```

Or, if you still want light merging:

```
Split Dispatch: ON
Required voice after tones: 1–2 seconds
Merge window: 15–20 seconds
```

### C) Voice often arrives late

```
Split Dispatch: ON
Required voice after tones: 3 seconds
Merge window: 45–75 seconds
```

---

## Troubleshooting

### Problem: “Calls are getting merged when they should not”

Try:
- **Lower the Merge window** (reduces how long the system waits and what it might merge)
- **Lower Required voice after tones** (fewer clips will be treated as “tones-only” and held)

---

### Problem: “Tones-only calls still appear by themselves”

Try:
- Turn **Split Dispatch ON**
- **Increase the Merge window** (if voice is arriving later than expected)
- **Increase Required voice after tones** slightly (so short tone clips are held more often)

---

### Problem: “Voice clips keep getting treated like tones-only”

Try:
- **Decrease Required voice after tones**
- Confirm your audio is clear enough for speech detection (very quiet or heavily clipped audio can look like “no voice”)

---

## Practical tips

- Start with conservative values and adjust gradually (small changes make a big difference).
- If a talkgroup is extremely busy, prefer a shorter **Merge window** to reduce accidental merges.
- If your system reliably sends a short tone burst and then a full voice dispatch, prefer a slightly higher **Required voice after tones** to keep tone-only clips from becoming their own calls.
