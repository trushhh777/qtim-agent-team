# Example project

Пользовательские правила примера сохраняются вне managed block.

<!-- qtim:contract:start -->
## Команда qtim

Подробный контракт: `.codex/team-charter.md`; роли: `.codex/agents/`; решения: `memory/`.
qtim workflow запускается только явным skill/delegation request. Main thread владеет fan-out,
проверяет advisory outputs и запускается на `gpt-5.6-sol` + `ultra`. Каждый ADR проходит
clean-context Sol adversary. После обновления используй `$qtim-update`, при сбое — `$qtim-doctor`.
<!-- qtim:contract:end -->
