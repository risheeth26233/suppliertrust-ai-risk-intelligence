import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECORDINGS = ROOT / "recordings" / "week02" / "voiceover"
SCENES = [
    (0.0, "scene-01.mp3", "Every supplier decision begins with incomplete information. A quote tells you a price; due diligence asks what supports the relationship. NIST's 2026 guide frames due diligence as research into pertinent supplier information before decisions, within ICT cyber supply chains. The OECD reports fewer than one in five large listed companies evaluate supplier risk against environmental or human-rights criteria.", None),
    (27.336, "scene-02.mp3", "SupplierTrust brings identity, recorded evidence, synthetic screening, explainable indicators, human review and a report into one traceable workspace.", None),
    (37.896, "scene-03.mp3", "The Command Center summarizes the available supplier records and review indicators. In the directory, we open Northstar Components, a fictional supplier created for this demonstration. The investigation workspace brings its profile into view. Risk Assessment shows a deterministic concern index. Expand a factor to see its recorded basis; this is not a probability of fraud. Evidence Explorer shows the source, reviewer, date and notes attached to a record; provenance adds context, but does not prove authenticity. Screening is explicitly synthetic. OFAC advises comparing full available details because many potential name matches are false positives. Performance and activity show only the observations and history in this fixture. The report gathers the current assessment and its limitations. We can preview it, then download the supported text report.", None),
    (93.312, "scene-04.mp3", "React presents the workflow. FastAPI serves the assessment and report logic. PostgreSQL supports the writable local application. The public demo uses a fixed fictional fixture.", None),
    (105.624, "scene-05.mp3", "One review path, recorded evidence, explainable indicators and reporting. But this demo is read-only.", 7.024),
]

def srt_time(value):
    ms = max(0, round(value * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def probe_duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], text=True).strip())

def pauses(path):
    result = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-38dB:d=0.22", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", result.stderr)]
    return list(zip(starts, ends))

all_captions, segments = [], []
for base, filename, text, trim in SCENES:
    path = RECORDINGS / filename
    if not path.exists():
        raise FileNotFoundError(path)
    full_duration = probe_duration(path)
    duration = trim if trim is not None else full_duration
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if trim is not None:
        sentences = sentences[:2]
    sentence_words = [len(re.findall(r"\b[\w'-]+\b", sentence)) for sentence in sentences]
    gaps = [gap for gap in pauses(path) if gap[0] > 0.15 and gap[1] < duration + 0.03]
    boundaries = []
    total_words = sum(sentence_words)
    cumulative = 0
    last_index = -1
    for count in sentence_words[:-1]:
        cumulative += count
        target = cumulative / total_words * duration
        options = [(abs(gap[0] - target), idx, gap) for idx, gap in enumerate(gaps) if idx > last_index and gap[0] > (boundaries[-1][1] if boundaries else 0) and gap[0] < duration - 0.25]
        if not options:
            raise RuntimeError(f"No pause aligned to a sentence boundary in {filename}")
        _, last_index, gap = min(options, key=lambda item: item[0])
        boundaries.append(gap)
    cue_start = 0.04
    for index, sentence in enumerate(sentences):
        cue_end = boundaries[index][0] - 0.04 if index < len(boundaries) else duration - 0.04
        if cue_end <= cue_start:
            raise RuntimeError(f"Invalid caption interval in {filename}")
        all_captions.append({"start": base + cue_start, "end": base + cue_end, "text": sentence})
        if index < len(boundaries):
            cue_start = boundaries[index][1] + 0.04
    segments.append({"storyStart": base, "file": filename, "duration": duration, "trimmed": trim is not None})

(HERE / "sentence-timing.json").write_text(json.dumps({"voice": "Microsoft Edge en-US-AndrewNeural", "rate": "-2%", "method": "Sentence ends estimated from silence gaps nearest to cumulative word-count targets; captions checked against the source text.", "segments": segments, "captions": all_captions}, indent=2), encoding="utf-8")
(HERE / "captions.json").write_text(json.dumps(all_captions, ensure_ascii=False, indent=2), encoding="utf-8")
srt = []
for index, item in enumerate(all_captions, 1):
    srt.extend([str(index), f"{srt_time(item['start'])} --> {srt_time(item['end'])}", item["text"], ""])
(ROOT / "final" / "SupplierTrust_Week02_Subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
print(f"Wrote {len(all_captions)} timed captions; final spoken cue ends at {all_captions[-1]['end']:.2f}s")
