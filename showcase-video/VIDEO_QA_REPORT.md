# SupplierTrust — final product and video QA

## A. Website quality

The website quality stage was completed before the new film was recorded. The existing production site remains at [suppliertrust-ai-risk-intelligence.vercel.app](https://suppliertrust-ai-risk-intelligence.vercel.app); the API remains at [suppliertrust-api-hp5b.onrender.com](https://suppliertrust-api-hp5b.onrender.com). No website, backend, Render, Neon, or deployment configuration was changed for this video pass.

- The Product Tour header fix separates its title, step count, and close control, fits constrained heights, supports all eight steps, and restores focus on close.
- The live browser capture was recorded from the production Vercel origin on 20 November 2026 at 1920×1080. It includes the corrected tour, Command Center, directory, investigation, risk, evidence, synthetic screening, performance, activity, report preview, and a real text-report download. Capture metadata records no page or console errors.
- The prior hosted regression covered seven investigation/report pages at eight viewport widths, all eight tour steps at 320×480, report preview/download, history, and no critical browser-console errors. The six API tests, frontend production build, motion checks, and 80 responsive page checks passed.
- Hosted checks confirmed `/healthz` and the database probe, fictional fixture reads, and blocked writes, uploads, screening refresh, reviewer decisions, private routes, and API documentation. The public demonstration remains fictional and read-only.
- Stage 1 was deployed as Vercel deployment `dpl_HZVSM5cahb5FM6B9fgnGuZaN2Ptn`. Commit [`dc00d0c`](https://github.com/risheeth26233/suppliertrust-ai-risk-intelligence/commit/dc00d0c95141d24abeb0e8ebcfc6a960e6b7c90a) passed [GitHub Actions run 44590034388](https://github.com/risheeth26233/suppliertrust-ai-risk-intelligence/actions/runs/44590034388).
- Automated axe testing was unavailable. Keyboard and focus behavior, touch use, reduced motion, and layout were checked through existing browser coverage and manual review; this is not a claim of full WCAG 2.2 AA conformance.

## B. Video production

### Deliverable and playback checks

- Master: `final/SupplierTrust_Week02_Research_Workflow_Demo.mp4`.
- FFprobe confirms H.264, 1920×1080, 30 fps, AAC stereo at 48 kHz, and an exact 120.000-second duration.
- Full FFmpeg decode completed successfully. The AAC master measures −16.2 LUFS integrated, 2.2 LU loudness range, and −1.5 dBFS true peak; the master does not exceed the configured true-peak ceiling.
- The separately supplied narration mix is 48 kHz, 24-bit stereo PCM. It was assembled from five Microsoft Edge `en-US-AndrewNeural` clips at native pitch and a `−2%` speaking rate. No pitch-shifting or metallic voice processing was applied.
- Voice signal was checked at the midpoint of all 22 caption cues: RMS ranged from −34.7 to −17.6 dBFS, median −22.5 dBFS. Silence detection also found natural pauses between phrases. This verifies speech activity throughout the written narration, not subjective voice quality.
- The 22 SRT cues are ordered and non-overlapping and cover the spoken lines through 112.608 seconds. Sentence boundaries are estimated from pauses nearest cumulative word-count targets, not forced-aligned at the phoneme level.
- The final mix retains the licensed Mixkit music bed, gently sidechains it under narration, and fades it at the end. Seven low-level, high-frequency-filtered UI clicks align with recorded navigation actions; one restrained paper slide accompanies the report. Effects do not trigger music ducking. Source audio files remain local and are not in Git; their license/source URLs are documented in `README.md`.

### Content, evidence, and visuals

- Independent research is distinguished from the product demonstration. The film attributes the NIST SP 1326 scope, OECD Figure 2.6 statistics, and OFAC FAQ 5 guidance on screen. Exact claims and qualifications are recorded in [`research/CLAIM_VERIFICATION.md`](research/CLAIM_VERIFICATION.md) and [`research/EVIDENCE_SOURCES.md`](research/EVIDENCE_SOURCES.md). None of those sources tested or endorses SupplierTrust.
- The film uses the fresh hosted browser capture from the verified production site. It labels the Northstar fixture and screening example as fictional/synthetic, shows the actual text-report download, and describes the deterministic score and product limitations without calling it an AI fraud prediction.
- Eleven representative frames from the finished film were inspected. The research opener, product reveal, hosted workflow, architecture, limitations, and end card are present. The captured public site contains no entered credentials or private supplier records.
- The previous cinematic video was preserved: `SupplierTrust_Week02_Cinematic_Refined.mp4` remains at SHA-256 `D387F4537B60B39C1D0C8669848BE33973C67E4D83CC92C8906BDBA78C682908`.
- The MP4, thumbnail, narration WAV, browser recording, and licensed source audio remain local and are excluded from Git. Source composition, capture/mix scripts, narration, captions, research notes, storyboard, and this report are versioned. The video was not published to LinkedIn.

### Remaining limitations

- No local ASR package or audio-listening input was available in this session. I verified TTS provenance, non-silent speech at each caption midpoint, timing, and measured audio levels, but did not subjectively audition tone, pronunciation, or intelligibility. The voice is neural TTS and may still sound synthetic; listen before public promotion.
- Caption boundaries are pause-based estimates and may be slightly early or late. The SRT is not phoneme-aligned.
- Automated axe testing was unavailable for the website checks; no full WCAG conformance claim is made.
- The final video binary and licensed source assets are not committed. Re-rendering requires restoring the ignored browser recording, TTS clips, music, and sound effects described in `README.md`.
