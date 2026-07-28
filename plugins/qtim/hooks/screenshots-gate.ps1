$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

try { $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
if ($payload.stop_hook_active -eq $true) { exit 0 }
$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) { $root = (Get-Location).Path }
$charter = Join-Path $root ".codex/team-charter.md"
if (-not (Test-Path -LiteralPath $charter -PathType Leaf)) { exit 0 }
$configPath = Join-Path $root ".codex/screenshots-gate.json"
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) { exit 0 }

try {
  $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
  $minutes = [int]$config.freshnessMinutes
} catch {
  [Console]::Error.WriteLine("qtim screenshot gate: invalid .codex/screenshots-gate.json: $($_.Exception.Message)")
  exit 2
}
if ($config.mode -ne "blocking") { exit 0 }
$directory = [string]$config.directory
if (-not $directory -or [IO.Path]::IsPathRooted($directory) -or
    ($directory -split '[\\/]' | Where-Object { $_ -eq '..' }) -or $minutes -le 0) {
  [Console]::Error.WriteLine("qtim screenshot gate: directory must be safe repo-relative and freshnessMinutes > 0")
  exit 2
}
$target = Join-Path $root $directory
$cutoff = [DateTime]::UtcNow.AddMinutes(-$minutes)
$fresh = $false
if (Test-Path -LiteralPath $target -PathType Container) {
  $fresh = @(Get-ChildItem -LiteralPath $target -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Extension.ToLowerInvariant() -in @(".png", ".jpg", ".jpeg", ".webp") -and
      -not $_.Name.StartsWith("front-selfcheck-") -and
      $_.LastWriteTimeUtc -ge $cutoff
    }).Count -gt 0
}
if ($fresh) { exit 0 }
[Console]::Error.WriteLine(
  "qtim screenshot gate: no fresh tester screenshots in $directory. Run the real-browser sweep and save PNG/JPG/WEBP evidence; if UI is objectively N/A, state that explicitly and finish once more."
)
exit 2
