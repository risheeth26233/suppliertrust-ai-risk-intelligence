# SupplierTrust Week 02 film

The research-backed product film is rendered from the React/Remotion composition in `production/week02/src/film.jsx`. The hosted workflow footage comes from `record_week02.mjs`; research citations and claim limits are in `research/`.

## Rebuild on Windows

The fresh browser recording, five Edge TTS voice clips, licensed music, and licensed sound effects are local production assets under `recordings/week02/` and are intentionally not committed. Restore or regenerate those assets before rendering. `generate_voiceover.py` analyzes the five existing voice clips and writes sentence timing, captions, and the SRT; it does not synthesize the clips. The voice used is Microsoft Edge `en-US-AndrewNeural` at `-2%` rate and native pitch.

```powershell
cd showcase-video/production/week02
npm ci
python generate_voiceover.py
$env:TEMP = Join-Path (Get-Location) '.remotion-tmp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
npm run render -- --chrome-mode=chrome-for-testing --browser-executable='C:\Program Files\Google\Chrome\Application\chrome.exe'
powershell -NoProfile -ExecutionPolicy Bypass -File .\mix_audio.ps1
```

`render` creates the intermediate silent H.264; `mix_audio.ps1` writes the final H.264/AAC MP4 and timed narration WAV. The SRT is generated from silence gaps in the voice clips, nearest to cumulative word-count targets, so sentence timing can vary slightly. The final mix uses seven filtered low-level clicks on the recorded navigation beats and a restrained paper slide as the report opens; music ducks under narration only. The thumbnail can be regenerated with `npm run thumbnail`. Final media, recordings, and render cache stay local to avoid committing licensed audio or large binary files. The video has not been published to LinkedIn.

## Music license

“Forest Mist Whispers” by Alejandro Magaña (A. M.), Mixkit record 148, is under the [Mixkit Stock Music Free License](https://mixkit.co/license/#musicFree). The license record is kept beside the local track; attribution is not required. The source MP3 is not redistributed in Git.

The click (“Slide click”, Mixkit 1130) and paper slide (“Paper slide”, Mixkit 1530) are covered by the [Mixkit Sound Effects Free License](https://mixkit.co/license/modal/sfxFree/). They are used only inside this film; the source WAVs are not committed or redistributed. Listing pages: [click](https://mixkit.co/free-sound-effects/click/?page=2) and [paper](https://mixkit.co/free-sound-effects/paper/).

## Deliverables

- `final/SupplierTrust_Week02_Research_Workflow_Demo.mp4` — local H.264/AAC master; excluded from Git.
- `final/SupplierTrust_Week02_Thumbnail.png` — local poster frame; excluded from Git.
- `final/SupplierTrust_Week02_Voiceover.wav` — local 48 kHz, 24-bit PCM narration mix; excluded from Git.
- `final/SupplierTrust_Week02_Subtitles.srt` — versioned 22-cue subtitle file.
- `VIDEO_QA_REPORT.md` — production and hosted-site verification, metrics, and limitations.
