$ErrorActionPreference = 'Stop'
$skillsRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }
$repoRoot = Split-Path -Parent $PSScriptRoot
$names = @('premium-product-ui', 'effects-only-motion')
$targets = $names | ForEach-Object { Join-Path $skillsRoot $_ }
foreach ($target in $targets) { if (Test-Path -LiteralPath $target) { throw "Refusing to overwrite existing skill: $target" } }
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
foreach ($name in $names) { Copy-Item -LiteralPath (Join-Path $repoRoot "skills\$name") -Destination (Join-Path $skillsRoot $name) -Recurse }
Write-Output "Installed: $($targets -join ', ')"
