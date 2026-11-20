$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$final = Join-Path $root 'final'
$voiceDir = Join-Path $root 'recordings\week02\voiceover'
$music = Join-Path $root 'recordings\week02\music\suppliertrust_week02_forest_mist_whispers.mp3'
$click = Join-Path $root 'recordings\week02\sfx\mixkit-1130-slide-click.wav'
$paper = Join-Path $root 'recordings\week02\sfx\mixkit-1530-paper-slide.wav'
$timing = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sentence-timing.json') -Raw | ConvertFrom-Json
$narration = Join-Path $final 'SupplierTrust_Week02_Voiceover.wav'
$inputs = @()
$filters = @()
for ($i = 0; $i -lt $timing.segments.Count; $i++) {
  $segment = $timing.segments[$i]
  $clip = Join-Path $voiceDir $segment.file
  if (-not (Test-Path -LiteralPath $clip)) { throw "Voice clip not found: $clip" }
  $inputs += @('-i', $clip)
  $length = ([double]$segment.duration).ToString('0.000', [cultureinfo]::InvariantCulture)
  $delay = [int][math]::Round($segment.storyStart * 1000)
  $filters += "[$i`:a]atrim=duration=$length,asetpts=PTS-STARTPTS,adelay=$delay`:all=1,volume=1.0[v$i]"
}
$voices = (0..($timing.segments.Count - 1) | ForEach-Object { "[v$_]" }) -join ''
$filters += "${voices}amix=inputs=$($timing.segments.Count):duration=longest:normalize=0,alimiter=limit=0.92,apad=whole_dur=120,atrim=0:120,asetpts=N/SR/TB[out]"
$graph = $filters -join ';'
& ffmpeg -y -hide_banner -loglevel error @inputs -filter_complex $graph -map '[out]' -c:a pcm_s24le -ar 48000 -ac 2 $narration
if ($LASTEXITCODE -ne 0) { throw 'Could not create the timed narration WAV' }
$silent = Join-Path $final 'SupplierTrust_Week02_silent.mp4'
$video = Join-Path $final 'SupplierTrust_Week02_Research_Workflow_Demo.mp4'
if (-not (Test-Path -LiteralPath $silent)) { throw "Silent Remotion render not found: $silent" }
if (-not (Test-Path -LiteralPath $music)) { throw "Licensed music not found: $music" }
if (-not (Test-Path -LiteralPath $click)) { throw "Licensed click effect not found: $click" }
if (-not (Test-Path -LiteralPath $paper)) { throw "Licensed paper effect not found: $paper" }
# Music ducks under narration only; the restrained foley stays audible without a metallic top end.
$filter = "[1:a]highpass=f=75,lowpass=f=14500,acompressor=threshold=-20dB:ratio=2.1:attack=18:release=180:makeup=1.2dB,alimiter=limit=0.95,asplit=2[sidechain][voice];[2:a]atrim=0:120,afade=t=in:st=0:d=3,afade=t=out:st=114:d=6,volume=0.14[music];[music][sidechain]sidechaincompress=threshold=0.035:ratio=5:attack=20:release=450[ducked];[3:a]atrim=0:0.363,highpass=f=140,lowpass=f=5200,volume=0.75,asplit=7[click1][click2][click3][click4][click5][click6][click7];[click1]adelay=45096:all=1[cue1];[click2]adelay=55896:all=1[cue2];[click3]adelay=63896:all=1[cue3];[click4]adelay=71896:all=1[cue4];[click5]adelay=78896:all=1[cue5];[click6]adelay=83896:all=1[cue6];[click7]adelay=89396:all=1[cue7];[4:a]atrim=0:1.094,highpass=f=120,lowpass=f=7000,volume=0.10,adelay=86896:all=1[paper];[voice][ducked][cue1][cue2][cue3][cue4][cue5][cue6][cue7][paper]amix=inputs=10:duration=longest:normalize=0,alimiter=limit=0.96,atrim=0:120,loudnorm=I=-16:TP=-1.5:LRA=7[a]"
& ffmpeg -y -hide_banner -loglevel error -i $silent -i $narration -i $music -i $click -i $paper -filter_complex $filter -map 0:v:0 -map '[a]' -c:v copy -c:a aac -b:a 256k -ar 48000 -t 120 -movflags +faststart $video
if ($LASTEXITCODE -ne 0) { throw 'Could not mux the final H.264/AAC film' }
Write-Output "Created $narration and $video"
