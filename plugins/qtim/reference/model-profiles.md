# Модельные профили qtim для Codex

Эта политика относится к custom agents, которые `$qtim-setup` копирует в `.codex/agents/*.toml`. Модель, reasoning и Fast главного task выбирает пользователь; qtim не переключает их скрыто.

## Профили по умолчанию

| Роль | Model / reasoning | Почему |
|---|---|---|
| architect | inherit session | архитектурные решения должны апгрейдиться вместе с выбранной пользователем frontier-моделью |
| database | inherit session | security/data-integrity требуют той же сильной модели, что ведёт основной task |
| frontend | inherit session | реализация и поведенческие развилки следуют текущему session profile |
| reviewer | inherit session | финальная трассировка не должна оставаться на приколоченном поколении |
| product | inherit session | intake и trade-offs следуют текущему session profile |
| testing | `gpt-5.6-terra` + `medium` | bounded QA-прогоны и сбор evidence выгоднее держать на явном более дешёвом профиле |

В Codex нет значения `model = "inherit"`. Наследование задаётся **отсутствием одновременно обоих полей** `model` и `model_reasoning_effort`. Не оставляй half-pair.

## Root reasoning и Ultra

- `Low` / `Medium` / `High` / `Extra High` / `Max` управляются пользователем в главном task. `Ultra` добавляет proactive delegation через subagents на поддерживаемых моделях.
- Вызов `$qtim-feature`, `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-onboard` или `$qtim-product-onboard` — явное разрешение на описанный skill workflow. `Ultra` не расширяет scope и не превращает любой запрос в full team-up.
- Не прописывай `max`, `ultra` или `service_tier = "fast"` в role templates по умолчанию. Child agents не поднимают qtim-команду рекурсивно; fan-out координирует main thread.
- Inherited role получает session model/reasoning, но не право менять execution depth A/B/C/D или user-selected scope.

## Явные пары и overrides

- Явный профиль всегда атомарен: `model` + `model_reasoning_effort` вместе.
- Template pair testing копируй дословно. Если точный slug недоступен, удали оба поля и наследуй session profile; не угадывай alias.
- Пользователь может pin любую роль явным catalog-supported override. `$qtim-update` показывает diff и не перезаписывает такой override молча.
- При миграции старые qtim-default pairs удаляй только когда они совпадают с известным template релиза; отличающаяся pair считается пользовательской до доказательства обратного.
- Профиль роли не определяет execution depth, число агентов или обязательность review.

Актуальные model slugs и возможности сверяй с официальными страницами [Models](https://developers.openai.com/codex/models) и [Subagents](https://developers.openai.com/codex/subagents), а доступность — с локальным runtime catalog.
