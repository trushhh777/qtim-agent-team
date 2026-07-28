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
@{
  systemMessage = "qtim: subagent завершился. Проверь реальные артефакты: изменённые файлы, отчёт, memory/, скриншоты/логи. Если артефактов нет — уточни у agent thread или проверь сам."
} | ConvertTo-Json -Compress
