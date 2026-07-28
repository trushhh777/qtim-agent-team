# Brainstorm: runtime-backed contracts qtim

## Problem Statement

**Что решаем:** критические правила qtim частично держатся на том, что агент сам откроет
charter, вспомнит migration contract или честно выполнит advisory gate. После обновления
рантайма такие допущения могут деградировать без видимого сигнала.

**Решение:** выбрать Codex-native механизмы, которые превращают общие принципы Claude qtim
1.12.0 в проверяемые контракты, не копируя Claude-specific runtime.

**Ограничения:** только Codex skills, custom-agent TOML, `AGENTS.md`, Codex hooks, repo-local
Python validators и generated project state. Без `.claude/*`, `Task*`, Claude agent-memory,
Agent Teams flags и скрытого fan-out.

**Критерии:** влияние на ложный успех (3×), проверяемость (3×), Codex-native соответствие
(2×), стоимость/риск внедрения (1×), обратная совместимость (1×).

## Diverge: 24 варианта

1. Записывать Handoff pointer последним атомарным completion marker.
2. Добавить отдельный `handoff.done` файл.
3. Считать Handoff завершённым по `Status: Approved`.
4. Встроить весь charter в каждый role TOML.
5. Встроить весь charter в корневой `AGENTS.md`.
6. Добавить короткий qtim-managed contract block в `AGENTS.md`.
7. Инжектировать весь charter через `SubagentStart`.
8. Инжектировать только напоминание прочитать charter через `SubagentStart`.
9. Создать короткий `.codex/team-contract.md` и ссылаться на него.
10. Добавить журнал `reference/runtime-compat.md`.
11. Выполнять runtime probe при каждом `$qtim-setup`.
12. Держать runtime assumptions только в maintainer `AGENTS.md`.
13. Закрепить reviewer через `sandbox_mode = "read-only"`.
14. Создать отдельную постоянную роль adversary.
15. Оставить read-only только текстовой инструкцией.
16. Добавить `{{DEV_CMD}}` и отдать запуск сервера tester.
17. Считать dev-сервер внешней обязанностью пользователя.
18. Добавить opt-in blocking screenshots gate на `SubagentStop`.
19. Сделать screenshots gate обязательным для всех проектов.
20. Проверять screenshots только reviewer-чеклистом.
21. Добавить diff-aware `check_migrations.py`.
22. Проверять migration notes только глазами на review.
23. Добавить полный generated-state golden + semantic validator.
24. Генерировать golden заново LLM-вызовом в CI.

## Cluster

### Атомарное состояние workflow

- 1–3: completion marker и resume-семантика Handoff.

### Доставка критического контекста

- 4–9: полный/сжатый contract через `AGENTS.md`, TOML или hooks.

### Наблюдаемость рантайма

- 10–12: отдельный журнал, setup-probe или maintainer-only заметки.

### Механические границы ролей

- 13–20: read-only enforcement, dev-server ownership и screenshots gate.

### Release и generated-state safety

- 21–24: migration CI и семантический golden.

## Converge

Шкала 1–10; итог — взвешенная нормализованная оценка.

| Решение | Ложный успех | Проверяемость | Codex-native | Стоимость | Совместимость | Итог |
|---|---:|---:|---:|---:|---:|---:|
| Pointer последним marker (1) | 10 | 10 | 10 | 10 | 10 | 10.0 |
| Managed contract в `AGENTS.md` (6) | 9 | 9 | 10 | 8 | 9 | 9.1 |
| Runtime compatibility journal (10) | 8 | 9 | 10 | 9 | 10 | 9.0 |
| Read-only reviewer (13) | 9 | 10 | 10 | 9 | 8 | 9.3 |
| `DEV_CMD` у tester (16) | 8 | 9 | 10 | 9 | 9 | 8.9 |
| Opt-in screenshots gate (18) | 9 | 10 | 9 | 6 | 9 | 8.8 |
| Migration CI (21) | 10 | 10 | 10 | 7 | 10 | 9.6 |
| Semantic golden (23) | 10 | 10 | 10 | 6 | 10 | 9.5 |
| Весь charter в `AGENTS.md` (5) | 8 | 8 | 9 | 6 | 5 | 7.6 |
| Весь charter через hook (7) | 8 | 7 | 8 | 4 | 6 | 6.9 |
| Обязательный screenshots gate (19) | 8 | 10 | 9 | 4 | 3 | 7.4 |
| LLM-regeneration golden в CI (24) | 7 | 3 | 6 | 2 | 4 | 4.8 |

## Selected

1. Атомарный Handoff marker: pointer пишется последним и участвует в resume.
2. Короткий qtim-managed contract в автоматически загружаемом `AGENTS.md`; charter остаётся
   детальным каноном и read-first fallback.
3. `reference/runtime-compat.md` с документированными фактами, probes и непроверенными границами.
4. Механические role contracts: reviewer read-only, tester владеет `DEV_CMD`, screenshots gate
   opt-in и блокирует максимум один раз.
5. Diff-aware migration CI и полный semantic golden generated state.

Дополнительно: разделить session orchestration `$qtim-feature` и долговечные artifact contracts
`feature-pipeline.md`; generated PM charter явно пометить производной сводкой.

## Runner-ups

- Короткий `.codex/team-contract.md`: вернуться, если managed block `AGENTS.md` станет слишком
  большим или столкнётся с пользовательскими override.
- `SubagentStart` additional context: использовать только после runtime probe и только для
  короткого сигнала, не для полного charter.

## Validation

- 24 варианта, 5 отличимых кластеров.
- Явные взвешенные критерии и сравнение выбранных альтернатив.
- Выбранные решения покрывают quick fix, runtime contract, role safety и release safety.
- Claude-only идеи и решения с высоким риском контекстного раздувания отсеяны явно.
