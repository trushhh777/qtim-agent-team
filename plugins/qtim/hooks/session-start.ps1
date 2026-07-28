$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

try { $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { $payload = $null }
$root = if ($payload -and $payload.cwd) { [string]$payload.cwd } else { [Environment]::CurrentDirectory }
while (-not (Test-Path -LiteralPath (Join-Path $root ".git"))) {
  $parent = Split-Path -Parent $root
  if (-not $parent -or $parent -eq $root) { break }
  $root = $parent
}
$charter = Join-Path $root ".codex/team-charter.md"
if (-not (Test-Path -LiteralPath $charter -PathType Leaf)) { exit 0 }
$match = Select-String -LiteralPath $charter -Pattern "qtim-version:\s*([0-9]+\.[0-9]+\.[0-9]+)" |
  Select-Object -First 1
$version = if ($match) { "v" + $match.Matches[0].Groups[1].Value } else { "legacy" }
$message = 'Команда Codex-агентов настроена. $qtim-feature — провести хотелку до PRD/оценки/плана, $qtim-team-up — эпик, $qtim-team-lazy — точечная задача, $qtim-update — проверить версию и обновить, $qtim-team-down — завершение активных agent threads.'
Write-Output ("[qtim {0}] {1}" -f $version, $message)
