---
name: qtim-team-retro
description: "Use when a qtim epic in Codex is finished (final review passed) or a large team session is ending: distill session facts (loops, blockers, recurring problem classes) into trigger -> action lessons in memory/retro-log.md and per-role sections of memory/lessons.md, before $qtim-team-down."
---

# qtim Team Retro

Ты проводишь ретроспективу завершённого эпика. Запускается после финального APPROVED reviewer'а или в конце большой сессии — **до** `$qtim-team-down`. Цель — превратить опыт эпика в записи памяти, которые сделают следующий эпик быстрее и чище.

Retro — для эпиков режима C/D (`$qtim-team-lazy` с эскалацией / `$qtim-team-up`); на тривиальных задачах (A/B) не запускается: дистиллировать нечего.

## Источники фактов (собери до анализа)

1. Видимый план/задачи сессии — что делалось, кто owner, что возвращалось на доработку.
2. `memory/review-report.md` — блокеры и рекомендации reviewer'а, вердикты, отклонённые findings.
3. `memory/bug-log.md` — что нашёл tester, в каком слое, сколько итераций занял фикс.
4. Результаты independent review — сколько findings подтверждено, сколько отброшено.
5. Собственный контекст сессии: где крутились петли impl -> test -> review, что затянуло.
6. «История изменений» планового документа фичи (`plan.md`, для fast-path — `feature-brief.md`) в `docs/features/<slug>/` — зафиксированные отклонения и новые edge cases.
7. Подтверждаемый diff текущего эпика: approved base/head, merge range или точный список changed files из проверенного handoff. Только в этом scope ищи `minimal-diff:`; repository-wide совпадения без связи с эпиком не приписывай текущей работе.

## Анализ — по фактам, не «как показалось»

- **Повторяющиеся классы проблем:** один тип блокера/бага >= 2 раз (например «забыт индекс на FK», «состояние не сброшено при смене scope») -> кандидат в урок роли-виновника.
- **Петли:** какие задачи прошли больше одного круга доводки и почему — нечёткая постановка, пропущенный инвариант, слабый self-check роли?
- **Что сработало:** приёмы, сэкономившие круг — закрепить как практику.
- **Шум:** правила/чеклисты, давшие ложные срабатывания — кандидаты на уточнение.

## Жатва `minimal-diff:` markers

Для каждого marker из подтверждённого epic diff приведи `path:line` и разбери
форму `потолок — проверяемый trigger и действие`.

Классифицируй по evidence:

- `triggered` — наблюдаемый trigger уже наступил; зафиксируй evidence;
- `not triggered` — trigger проверен и ещё не наступил;
- `unknown` — доступных данных недостаточно;
- `malformed` — нет проверяемого trigger или действия;
- `protected violation` — marker пытается отложить trust-boundary validation,
  защиту от потери данных, security/access, базовую accessibility, explicit
  user behavior, approved acceptance criterion или documented invariant.

Только `triggered` создаёт durable follow-up. Запиши его в текущий
`memory/retro-log.md`: exact marker и source, trigger evidence, ровно один owner,
проверяемое next action. `not triggered` и `unknown` покажи в отчёте без
backlog-задачи; `malformed` верни автору как рекомендацию исправить marker;
`protected violation` — нарушение исходного contract, а не легализованный долг.
Не создавай внешний issue, новый backlog или другой memory-файл без отдельной
просьбы пользователя.

Перед записью проверь существующий retro-log по паре source + exact marker.
Не дублируй follow-up без нового trigger evidence или изменившегося next action.

## Дистилляция — два уровня записи

Всю память пишет main thread (субагенты в `memory/` не пишут).

1. **Проектная память:** запись в `memory/retro-log.md` (создай при первом retro): дата · эпик · 1-3 строки метрик (задач / кругов доводки / блокеров) · уроки списком «триггер -> действие» · triggered `minimal-diff:` follow-up по contract выше. Обнови индекс `memory/MEMORY.md`.
2. **Уроки ролей:** урок, адресованный конкретной роли, — в `memory/lessons.md` в секцию `## qtim-<role>` (создай файл/секцию при необходимости). Роли читают свою секцию при спавне (prompt template `$qtim-team-up` включает её в read-first), поэтому уроки доживают до следующей сессии, хотя agent threads — нет.

**Критерий качества урока:** конкретный триггер + конкретное действие («у словарей этого проекта уникальность per-scope — проверяй partial unique до написания миграции»), а не пожелание («внимательнее с миграциями»). Урок, дублирующий `AGENTS.md`/charter или прошлый retro, не записывается. Устаревшие уроки прошлых retro — удаляй: память не свалка.

## Отчёт пользователю

3-5 уроков + метрики эпика + classification каждого epic-scoped marker + что
записано куда. Результатом, не процессом.

## Anti-Patterns

- Retro на тривиальной задаче (режим A/B).
- Урок-вода без триггера и действия.
- Дублировать в память то, что уже в `AGENTS.md` / charter / прошлых уроках.
- Пересказ хронологии эпика вместо паттернов.
- Озвучить уроки в тред и не записать в файлы — после сессии они исчезнут.
- Искать markers по всему репозиторию и выдавать старую заметку за результат эпика.
- Создавать follow-up для `not triggered`/`unknown` или принимать marker в protected zone.
