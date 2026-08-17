# Продуктовый словарь qtim

| Термин | Пользовательское значение | Связи и состояния | Канон |
|---|---|---|---|
| Track | Совместимая дорожка роли пользователя: dev реализует, PM готовит handoff | Setup добавляет dev, PM или обе; re-run не стирает соседний block | `plugins/qtim/skills/qtim-setup/SKILL.md:72-90,130-144` |
| Team shape / roster | Набор доступных custom roles, адаптированный под стек | Dev выбирает Compact/Standard/Extended; PM consult roster определяется стеком | `plugins/qtim/skills/qtim-setup/SKILL.md:80-90,159-168` |
| Execution depth A–D | Стоимость координации, а не число roles | A main, B one agent, C one-pass lazy, D iterative team-up | `plugins/qtim/reference/orchestration-patterns.md:7-25` |
| Intake | Зафиксированное понимание проблемы, пользователя, outcome, success, constraints и non-goals | Заканчивается выбором fast/full track | `plugins/qtim/skills/qtim-feature/SKILL.md:26-39` |
| Fast-path | Планирование S/M одной фазы без Fork Test | `intake.md -> feature-brief.md -> approval -> lazy handoff` | `plugins/qtim/skills/qtim-feature/SKILL.md:39-57` |
| Full track | Планирование L/XL, нескольких фаз или decision fork | `intake -> PRD -> decomposition+estimate -> plan -> handoff` | `plugins/qtim/skills/qtim-feature/SKILL.md:59-105` |
| Artifact | Versioned документ фичи в `docs/features/<slug>/` | `Draft -> Approved -> In Development -> Done`; history append-only | `plugins/qtim/reference/feature-pipeline.md:16-38` |
| Checkpoint | Явное решение пользователя о текущем artifact/scope | Intake; PRD; общий decomposition+estimate; plan; один brief approval для fast | `plugins/qtim/reference/feature-pipeline.md:40-51` |
| Handoff | Утверждённый единый источник scope/criteria/gates для реализации | Full -> team-up/lazy; fast -> lazy; decision registry получает pointer | `plugins/qtim/reference/feature-pipeline.md:94-100` |
| DRI | Один владелец главной acceptance boundary work item | Синтезирует итог item и отвечает за вертикальную проверяемость | `plugins/qtim/reference/feature-pipeline.md:75-92` |
| Contributing role/layer | Участник, дающий evidence и оценку своего slice | Не становится совладельцем DRI и не требует автоматического fan-out | `plugins/qtim/skills/qtim-feature/SKILL.md:43,67-78` |
| S/M/L/XL | Относительный размер работы, не часы/дни | Confidence + risks обязательны; XL означает разрезать item | `plugins/qtim/reference/feature-pipeline.md:85-92` |
| Confidence | Уверенность в grounded estimate | Обязательное поле рядом с evidence/risk; шкала уровней пока не определена | `plugins/qtim/skills/qtim-feature/SKILL.md:74-78` |
| Evidence | Проверяемая опора: files, coverage, integration point, git/memory reference class | Estimate или finding без evidence не принимается | `plugins/qtim/skills/qtim-feature/SKILL.md:67-78`, `plugins/qtim/reference/independent-review.md:45-70` |
| Memory | Durable knowledge между задачами, не chat/thread state | Engineering и product memory разделены; main thread пишет и дедуплицирует | `plugins/qtim/skills/qtim-onboard/SKILL.md:37-50`, `plugins/qtim/skills/qtim-product-onboard/SKILL.md:42-63` |
| Epic state | Handoff незавершённой C/D работы | Создаётся team-down; читается team-up; удаляется после завершения | `plugins/qtim/skills/qtim-team-down/SKILL.md:8-31` |
| Retro / lesson | Проверенный урок прошедшего эпика | Retro до down; `retro-log.md` + role-specific `lessons.md` | `plugins/qtim/skills/qtim-team-retro/SKILL.md:6-39` |
| ADR | Отдельный документ для consequential, дорогого в откате trade-off | Иначе строка decision registry; до approval два stress-test pass | `plugins/qtim/agents/architect.toml:23-42` |
| Grill | Первый, контекстный stress-test плана/ADR | Не заменяет независимого adversary | `plugins/qtim/reference/intake-protocol.md:62,77-85` |
| ADR adversary | Новый clean-context read-only Sol thread | `xhigh`; `max` iff irreversible + documented invariant; skipped не pass | `plugins/qtim/reference/independent-review.md:14-27` |
| Independent code review | Risk-based read-only review фактического diff | Mandatory high-risk; low-risk может иметь явный skip; не равен ADR gate | `plugins/qtim/reference/independent-review.md:29-44` |
| Hook layer | Plugin lifecycle events и optional project reminder | Plugin: SessionStart/SubagentStop; project: PostToolUse; `/hooks` trust | `plugins/qtim/skills/qtim-setup/SKILL.md:170-184` |
| Version stamp | Версия generated charter/agent state | Update повышает только после полностью applied migration | `plugins/qtim/skills/qtim-update/SKILL.md:10-15,34-53` |
| Pending migration | Неприменённый или неоднозначный upgrade step | Останавливает дальнейшие версии; stamps остаются на последней complete | `plugins/qtim/skills/qtim-update/SKILL.md:38-43` |
| Model override | Пользовательская atomic pair вместо qtim default | Сохраняется после показанного diff; unavailable slug не угадывается | `plugins/qtim/reference/model-profiles.md:28-33` |
| Explicit workflow authorization | Skill invocation/direct delegation разрешает bounded fan-out | Не создаёт persistent team и не расширяет scope | `plugins/qtim/reference/model-profiles.md:23-25` |

## Текущая policy отменяет исторические формулировки

- 2.9 inheritance superseded explicit GPT-5.6 pairs 2.10: `CHANGELOG.md:5-19,43-49`.
- Project copies `SessionStart`/`SubagentStop` superseded plugin-bundled ownership; project оставляет optional `PostToolUse`: `CHANGELOG.md:65-73`, `plugins/qtim/reference/upgrade-notes.md:69-87`.
- «Independent review можно выключить» относится только к code diff; ADR adversary остаётся обязательным: `CHANGELOG.md:15-18`.
- Separate decomposition/estimate checkpoints superseded общим checkpoint; fast-path стал полноценной веткой: `plugins/qtim/reference/feature-pipeline.md:40-51`.

## Неопределённая лексика

Это белые пятна, не установленные правила:

- Нет коротких user-facing критериев выбора Compact/Standard/Extended.
- Граница C/D описана loops/escalation triggers, но не имеет единой cost/risk rubric.
- Для `confidence` нет шкалы или semantics уровней.
- Не определено, кто и когда архивирует отменённый approved feature pointer.
- `approval` и `checkpoint` не определяют единообразно допустимый scope изменения без возврата статуса в Draft.
