# Модельные профили qtim для Codex

Эта политика относится к custom agents, которые `$qtim-setup` копирует в `.codex/agents/*.toml`. Модель и reasoning главного task пользователь выбирает в Codex; qtim не переключает их скрыто.

## Профили по умолчанию

| Роль | Model | Reasoning | Почему |
|---|---|---|---|
| architect | `gpt-5.6-sol` | `high` | неоднозначные архитектурные решения, планирование и проверка инвариантов |
| database | `gpt-5.6-sol` | `high` | миграции, авторизация и data-integrity требуют проверки edge cases |
| frontend | `gpt-5.6-sol` | `medium` | реализация и computer/browser work с балансом глубины и скорости |
| testing | `gpt-5.6-terra` | `medium` | bounded QA-прогоны, сбор evidence и локализация дефектов |
| reviewer | `gpt-5.6-sol` | `high` | независимая трассировка логики, рисков и пропущенных гейтов |
| product | `gpt-5.6-sol` | `high` | неоднозначный intake, синтез evidence и продуктовые trade-offs |

Используй точные catalog slugs из templates. Не сокращай `gpt-5.6-sol` до догаданного алиаса: сгенерированный TOML должен стартовать воспроизводимо.

## Root reasoning и Ultra

- `Low` / `Medium` / `High` / `Extra High` / `Max` управляются пользователем в главном task. `Max` даёт больше reasoning одному task; `Ultra` добавляет proactive delegation через subagents на поддерживаемых моделях.
- Вызов `$qtim-feature`, `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-onboard` или `$qtim-product-onboard` — явное разрешение на описанный в skill subagent workflow. Выбранный пользователем `Ultra` не расширяет scope и не превращает любой запрос в full team-up.
- Не прописывай `max` или `ultra` в role templates по умолчанию. Роли получают `high`/`medium`, а fan-out координирует main thread. Child agents не должны рекурсивно спавнить команду; если нужны дополнительные роли, их спавнит main thread.
- Не добавляй `service_tier = "fast"` в role templates без явного выбора пользователя: Fast меняет расход credits и остаётся настройкой task/session.

## Совместимость и overrides

- `model` и `model_reasoning_effort` — одна профильная пара. Если точный model slug недоступен в окружении, удали **оба** поля: роль унаследует модель и reasoning главного task.
- Явный пользовательский override модели или reasoning не перезаписывай молча при `$qtim-update`: покажи diff и сохрани override, если пользователь не выбрал профиль 2.7.0.
- Не заменяй недоступную модель догаданным слагом. Безопасный fallback — полное наследование пары от main thread.
- Профиль роли не определяет execution depth A/B/C/D. Глубину координации выбирает main thread по задаче, а не по модели, reasoning или числу доступных агентов.

Актуальные термины и возможности сверяй с официальными страницами [Models](https://developers.openai.com/codex/models) и [Subagents](https://developers.openai.com/codex/subagents).
