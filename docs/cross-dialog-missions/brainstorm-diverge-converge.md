# Brainstorm: cross-dialog missions qtim

Дата: 2026-07-28
Статус: Draft

## Problem Statement

**Что решаем:** qtim координирует subagents внутри одной задачи Codex, но не умеет
из одного явно вызванного workflow создать несколько видимых peer-задач Codex,
отслеживать DAG-зависимости, передавать между задачами проверенные результаты,
интегрировать их изменения и закрывать миссию общим verification gate.

**Решение:** выбрать Codex-native архитектуру `$qtim-mission`, совместимую с
репозиторием без application runtime. Полный режим должен использовать доступные
в Codex App thread tools; на поверхностях без них workflow обязан fail-visible
перейти к single-thread/subagent fallback, а не имитировать созданные диалоги.

**Ограничения:**

- qtim остаётся Markdown/JSON/TOML-плагином без собственного daemon, MCP-сервера,
  app-server клиента или tmux runtime;
- создание peer-задач разрешено только явным executable `$qtim-mission` или
  недвусмысленной просьбой провести несколько Codex peer tasks как одну mission;
- mission coordinator единолично владеет графом; worker-задачи не создают
  дочерние qtim-миссии;
- agent/thread handles считаются runtime hints, а не скрытым persistent team state;
- project decisions и verification evidence остаются в `memory/`;
- write-задачи изолируются worktrees; parallel writers в одном checkout запрещены;
- пользовательские approvals и продуктовые развилки не подтверждаются автоматически.

**Критерии выбора:**

1. Пользовательская полнота mission flow — вес 3.
2. Codex-native соответствие — вес 3.
3. Совместимость с «нет application runtime» — вес 2.
4. Восстановление после прерывания — вес 2.
5. Проверяемость и fail-visible поведение — вес 2.
6. Стоимость и риск внедрения — вес 1.

## Diverge: 30 вариантов

1. Один skill `$qtim-mission` с режимами start/resume/status/stop.
2. Четыре skills: mission-start, mission-resume, mission-status, mission-down.
3. Расширить `$qtim-team-up` peer-задачами вместо нового публичного входа.
4. Создавать peer-задачи через доступный App `create_thread`.
5. Делать same-directory forks текущего диалога.
6. Использовать только существующих subagents и переименовать их «диалогами».
7. Запускать каждую node как cloud task.
8. Управлять миссией через собственный Codex app-server клиент.
9. Добавить qtim MCP server с scheduler и state database.
10. Использовать heartbeat automations как scheduler.
11. Создавать все worker-задачи сразу и держать зависимые в ожидании.
12. Создавать worker-задачу только когда все её зависимости готовы.
13. Хранить DAG только в контексте coordinator-диалога.
14. Хранить portable mission spec и evidence в `memory/missions/<slug>/`.
15. Хранить runtime handles в `.codex/qtim-runtime/missions/<slug>.json`.
16. Хранить thread ids прямо в коммитируемом `memory/`.
17. Восстанавливать handles только по префиксу title через `list_threads`.
18. Передавать downstream-задаче полный transcript upstream-задачи.
19. Передавать bounded context pack через initial prompt.
20. Передавать follow-up через `send_message_to_thread`.
21. Канонизировать результат каждой node как worker receipt.
22. Передавать code changes через общий checkout.
23. Передавать code changes через commit SHA из worker worktree.
24. Интегрировать изменения через native `handoff_thread`.
25. Интегрировать commits последовательным cherry-pick в coordinator checkout.
26. Проверять каждую node собственным локальным gate до unlock downstream.
27. Делать только один общий review в конце миссии.
28. Создавать отдельную clean-context verification-задачу после интеграции.
29. При NOT APPROVED строить fix nodes и повторять bounded verification loop.
30. Автоматически архивировать worker-задачи сразу после завершения.

## Cluster

### Публичный workflow и control plane

- 1–3: один mission skill, набор lifecycle skills или расширение team-up.
- 8–10: skill-only orchestration против отдельного runtime/scheduler.

### Создание и планирование peer-задач

- 4–7: App threads, forks, subagents или cloud tasks.
- 11–12: eager creation против wave-based DAG scheduling.

### Durable и runtime state

- 13–17: chat-only state, portable memory, local runtime registry или title discovery.

### Передача результатов и кода

- 18–25: transcript/context packs/receipts и shared checkout/commit/handoff.

### Verification и lifecycle

- 26–30: per-node gates, clean-context final review, fix loops и cleanup.

## Converge: архитектурные варианты

Шкала 1–10. Итог — взвешенная нормализованная оценка по критериям выше.

| Вариант | Mission flow | Codex-native | Без runtime | Recovery | Проверяемость | Стоимость | Итог |
|---|---:|---:|---:|---:|---:|---:|---:|
| A. Skill + App thread tools + split state | 9 | 10 | 10 | 8 | 9 | 8 | 9.2 |
| B. Только subagents в одной задаче | 5 | 10 | 10 | 6 | 8 | 10 | 7.8 |
| C. qtim MCP scheduler | 10 | 8 | 2 | 10 | 10 | 3 | 7.7 |
| D. Собственный app-server client | 10 | 7 | 1 | 10 | 10 | 2 | 7.2 |
| E. Heartbeat/automation scheduler | 7 | 8 | 8 | 9 | 7 | 5 | 7.6 |

## Selected

### 1. Один `$qtim-mission`

Skill содержит режимы `start`, `resume`, `status`, `stop`, но сам определяет их из
намерения пользователя. Это один discoverable entrypoint, а не четыре почти
одинаковых публичных skills.

### 2. App-first thread adapter

Полный режим использует capability detection и только доступные нативные операции:

- `list_projects`;
- `create_thread`;
- `list_threads`;
- `read_thread`;
- `wait_threads`;
- `send_message_to_thread`;
- `set_thread_title`;
- `handoff_thread` + status, когда integration mode его требует.

На поверхности без `create_thread`/`wait_threads` workflow предлагает явный
single-task fallback через `$qtim-team-up`/subagents. Он не сообщает, что создал
peer-диалоги.

### 3. Wave-based DAG

Coordinator создаёт только ready nodes. Downstream-задача получает уже проверенный
context pack зависимостей в initial prompt. Это дешевле и надёжнее, чем создавать
заблокированные задачи заранее и затем пытаться синхронизировать их контекст.

### 4. Split state

- `memory/missions/<slug>/` — portable mission spec, decisions, receipts и
  verification evidence;
- `.codex/qtim-runtime/missions/<slug>.json` — локальные thread/host ids, cursors,
  attempts и last-known runtime status.

Расположение runtime state и его gitignore policy требуется утвердить отдельным ADR
до реализации generated-state migration.

### 5. Receipt + commit/handoff transport

Каждая node возвращает компактный проверяемый receipt. Текстовые результаты
передаются bounded context pack. Writer-задача работает в worktree и возвращает
commit SHA; основной integration path выбирается ADR между native handoff и
последовательным commit integration.

### 6. Отдельный финальный verifier

После интеграции coordinator создаёт clean-context read-only verification-задачу.
`APPROVED` возможен только при зелёных mission acceptance criteria и project gates.
`NOT APPROVED` создаёт bounded fix nodes; бесконечный loop запрещён.

## Runner-ups

- **MCP scheduler:** вернуться только если skill-only state окажется недостаточно
  надёжным после реального App MVP. Это отдельное изменение архитектуры продукта.
- **Automations:** использовать позже для напоминаний о stalled mission, а не как
  основной dependency scheduler.
- **Title-only recovery:** оставить последним fallback; одинаковые titles и смена
  host делают его недостаточно надёжным как единственный источник истины.
- **Несколько lifecycle skills:** вернуться, если один `$qtim-mission` станет слишком
  большим для discoverability или проверки.

## Validation

- Сгенерировано 30 вариантов в 5 отличимых кластерах.
- Сравнено 5 архитектурных подходов по 6 взвешенным критериям.
- Выбранный вариант выполняет запрос пользователя без нового application runtime.
- App-only границы и degraded mode названы явно.
- Runtime handles отделены от portable project knowledge.
- Параллельная запись, approvals, recovery и финальная верификация имеют отдельные
  fail-visible контракты.

Самооценка по rubric Brainstorm Diverge-Converge: **4.4/5** — количество 4,
разнообразие 5, креативность 4, качество/покрытие кластеров 4/4, ясность критериев
5, строгость scoring 4, качество выбора 4, actionable plan 5, целостность процесса 5.
