$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$python = (Get-Command python).Source
$node = (Get-Command node).Source
$runId = [guid]::NewGuid().ToString('N')
$db = Join-Path $env:TEMP ("suppliertrust-browser-$runId.db")
$portFinder = { $listener=[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,0); $listener.Start(); $port=$listener.LocalEndpoint.Port; $listener.Stop(); $port }
$apiPort=& $portFinder; $uiPort=& $portFinder; $demoPort=& $portFinder
while ($uiPort -eq $apiPort) { $uiPort=& $portFinder }; while ($demoPort -in @($apiPort,$uiPort)) { $demoPort=& $portFinder }
$apiLog = Join-Path $env:TEMP "suppliertrust-browser-$runId-api.log"
$apiErr = Join-Path $env:TEMP "suppliertrust-browser-$runId-api.err.log"
$uiLog = Join-Path $env:TEMP "suppliertrust-browser-$runId-ui.log"
$uiErr = Join-Path $env:TEMP "suppliertrust-browser-$runId-ui.err.log"
$demoLog = Join-Path $env:TEMP "suppliertrust-browser-$runId-demo.log"
$demoErr = Join-Path $env:TEMP "suppliertrust-browser-$runId-demo.err.log"
$api = $null; $ui = $null; $demo = $null
try {
    $env:SUPPLIERTRUST_DB = $db
    $env:SUPPLIERTRUST_MODE = 'local'
    $env:SUPPLIERTRUST_ALLOWED_ORIGINS = "http://127.0.0.1:$uiPort,http://127.0.0.1:$demoPort"
    python tests/seed_browser_db.py
    $api = Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',"$apiPort") -WorkingDirectory $root -PassThru -WindowStyle Hidden -RedirectStandardOutput $apiLog -RedirectStandardError $apiErr
    $vite = Join-Path $root 'frontend/node_modules/vite/bin/vite.js'
    $env:VITE_DEMO_MODE = 'false'; $env:VITE_API_URL = "http://127.0.0.1:$apiPort"
    $ui = Start-Process -FilePath $node -ArgumentList @($vite,'--host','127.0.0.1','--port',"$uiPort",'--strictPort') -WorkingDirectory (Join-Path $root 'frontend') -PassThru -WindowStyle Hidden -RedirectStandardOutput $uiLog -RedirectStandardError $uiErr
    $env:VITE_DEMO_MODE = 'true'
    $demo = Start-Process -FilePath $node -ArgumentList @($vite,'--host','127.0.0.1','--port',"$demoPort",'--strictPort') -WorkingDirectory (Join-Path $root 'frontend') -PassThru -WindowStyle Hidden -RedirectStandardOutput $demoLog -RedirectStandardError $demoErr
    Remove-Item Env:VITE_DEMO_MODE,Env:VITE_API_URL
    $ready = $false
    for ($i=0; $i -lt 30; $i++) {
        try {
            $null = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$apiPort/healthz" -TimeoutSec 2
            $null = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$uiPort/" -TimeoutSec 2
            $null = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$demoPort/" -TimeoutSec 2
            $ready = $true; break
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $ready) {
        foreach ($log in @($apiLog,$apiErr,$uiLog,$uiErr,$demoLog,$demoErr)) { if (Test-Path $log) { Write-Host "--- $log"; Get-Content -LiteralPath $log -Tail 20 } }
        throw 'Local test servers did not start.'
    }
    $env:PW_CHANNEL = if (Test-Path 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe') { 'msedge' } elseif (Test-Path 'C:\Program Files\Google\Chrome\Application\chrome.exe') { 'chrome' } else { '' }
    $env:SUPPLIERTRUST_FRONTEND_URL = "http://127.0.0.1:$uiPort"
    $env:SUPPLIERTRUST_DEMO_URL = "http://127.0.0.1:$demoPort"
    node tests/browser.mjs
    if ($LASTEXITCODE -ne 0) { throw "Browser integration workflow failed with exit code $LASTEXITCODE" }
} finally {
    foreach ($process in @($api,$ui,$demo)) { if ($process -and -not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue } }
    Remove-Item Env:SUPPLIERTRUST_DB,Env:SUPPLIERTRUST_MODE,Env:SUPPLIERTRUST_ALLOWED_ORIGINS,Env:PW_CHANNEL,Env:SUPPLIERTRUST_FRONTEND_URL,Env:SUPPLIERTRUST_DEMO_URL -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $db,$apiLog,$apiErr,$uiLog,$uiErr,$demoLog,$demoErr -Force -ErrorAction SilentlyContinue
}
