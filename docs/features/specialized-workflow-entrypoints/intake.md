Feature: Специализированные workflow-входы qtim
Slug: specialized-workflow-entrypoints
Status: Approved
Дата: 2026-07-27

# Intake

## Проблема и пользователи

В qtim 2.10 нет специализированных входов для security review, починки build/CI, проверки контрактов, измеренной оптимизации производительности и TDD-режима. Пользователь вынужден вручную собирать эти процессы из существующих ролей и дисциплин либо ошибочно воспринимает их как недостающие постоянные роли.

Проблему испытывают разработчики и технические лиды, которые хотят запустить узкий воспроизводимый workflow с предсказуемыми гейтами и форматом результата, сохранив компактный проектный roster.

## Желаемый результат

Добавить пять явно вызываемых Codex skills/workflows:

- `$qtim-security-review` — read-only аудит с findings P0–P3, evidence `file:line`, сценарием эксплуатации, владельцем исправления и вердиктом `APPROVED / NOT APPROVED`;
- `$qtim-build-fix` — воспроизводимая диагностика и минимальная починка build, typecheck, lint или CI с повтором исходной и связанных проверок;
- `$qtim-contract-review` — проверка производителей и потребителей контрактов, breaking-классификация, несовместимые call sites, migration/expand-contract план и необходимые contract/regression tests;
- `$qtim-performance` — поиск и минимальная починка только измеренной проблемы с baseline, бюджетом, профилем/trace/benchmark и сравнением до → после;
- `$qtim-tdd` — режим выполнения поведения через короткий цикл `RED → GREEN → REFACTOR → VERIFY`.

Каждый skill координирует только нужные существующие роли из project charter (`architect`, `database`, `frontend`, `testing`, `reviewer` и профильного исполнителя), когда они реально присутствуют и затронуты. Main thread владеет fan-out; skills не создают скрытую постоянную команду и не добавляют пять новых TOML-агентов.

## Связь с текущим qtim

| Workflow | Переиспользуемая основа |
|---|---|
| Security review | high-risk matrix + reviewer + database при наличии DB-слоя |
| Build fix | `$qtim-debug-loop` + владелец сломанного слоя |
| Contract review | architect + reviewer + expand-contract |
| Performance | `$qtim-debug-loop` + database/frontend/testing по измеренному bottleneck |
| TDD | testing + профильный исполнитель + reviewer |

Новые skills должны оставаться orchestration-входами и переиспользовать существующие инварианты, role ownership, debug discipline и review contracts вместо их независимого дублирования.

## Критерии успеха

- Плагин содержит пять discoverable skills с чёткими trigger/description и self-contained workflow-контрактами.
- Ни в plugin templates, ни в generated project state не появляются новые постоянные роли для этих workflow.
- Каждый skill явно определяет preconditions, selective roster, write/read-only границы, этапы, verification gates, формат результата, escalation и anti-patterns.
- `$qtim-security-review` никогда не меняет production-код без отдельной просьбы пользователя.
- `$qtim-build-fix` не маскирует ошибку отключением gates и не обновляет зависимости без доказанной причины.
- `$qtim-contract-review` прослеживает contract producer → consumers и классифицирует совместимость.
- `$qtim-performance` не предлагает и не вносит оптимизацию без baseline и повторного измерения.
- `$qtim-tdd` требует подтверждённый RED до production-изменения и связанные regression gates после GREEN/REFACTOR.
- Selective orchestration соблюдает main-thread fan-out, runtime thread cap, точные model pairs и отсутствие recursive child-team spawning.
- Repo-local validation, plugin validation и проверка документации проходят; release notes и upgrade notes соответствуют влиянию на generated state.

## Ограничения и совместимость

- Репозиторий остаётся Codex-native; Claude primitives и пять новых agent TOML запрещены.
- Источник истины — текущий repository и qtim 2.10.0; изменение должно быть совместимо с существующими `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-debug-loop`, charter и high-risk review matrix.
- Production-код этого репозитория отсутствует: реализация фичи затрагивает Markdown/JSON/TOML, validators и release/migration документацию.
- Пять skills являются публичными входами, поэтому изменение требует version bump и `CHANGELOG.md`.
- Если меняется сгенерированный project charter или другая `.codex/*`-поверхность, требуется явная миграция в `plugins/qtim/reference/upgrade-notes.md`; иначе там фиксируется «миграция не требуется».
- Срок не задан; приоритет — корректность контрактов и проверяемость, а не минимальное число файлов.

## Вне scope

- Пять новых постоянных custom-agent ролей или TOML templates.
- Скрытое переключение model/reasoning уже открытой Codex-задачи.
- Рекурсивный fan-out дочерними агентами или обещание persistent team state.
- Автоматическое исправление findings из `$qtim-security-review`.
- «Зелёный CI» через отключение lint/typecheck/tests, массовые suppressions или слепое обновление зависимостей.
- Оптимизация без измеримого сценария, baseline и повторного замера.
- Замена общих `$qtim-team-up`, `$qtim-team-lazy` и `$qtim-debug-loop`.
- Одновременная текстовая копия реализации в Claude sibling; возможен отдельный последующий семантический порт по `docs/claude-port-map.md`.

## Выбранный путь

Полный трек: фича добавляет пять публичных workflow-контрактов, затрагивает orchestration, validation, документацию релиза и, возможно, generated-state migration. Ожидается несколько work items и verification phases.

## Открытые вопросы checkpoint

1. Подтвердить write-policy: `$qtim-build-fix`, `$qtim-performance` и `$qtim-tdd` могут менять production-код в пределах явного scope вызова; `$qtim-contract-review` по умолчанию read-only и выдаёт план, как `$qtim-security-review`.
2. Подтвердить интеграцию: каждый новый skill является самостоятельным явным входом, но при необходимости использует существующие qtim subagents напрямую; он не обязан сначала вызывать `$qtim-team-up`/`$qtim-team-lazy`.
3. Подтвердить release scope: сейчас проектируем и реализуем только Codex plugin; семантический порт в `../qtim-agent-team-claude` остаётся отдельной следующей задачей.
4. Есть ли дополнительное ограничение по backward compatibility для проектов, уже настроенных на qtim 2.10, кроме миграции через `$qtim-update` при изменении generated state?

## История изменений

- 2026-07-27 — Draft: исходная хотелка преобразована в intake; зафиксированы пять workflow-входов, запрет новых ролей, критерии успеха и открытые продуктовые развилки.
- 2026-07-27 — Approved: пользователь подтвердил write-policy, прямую selective orchestration, Codex-only scope и совместимость через `$qtim-update`.
