---
name: qtim-minimal-diff
description: "Use before a non-trivial design or implementation choice, and whenever a change is gaining a new abstraction, layer, dependency, duplicate helper, or speculative flexibility: choose the smallest complete solution with a seven-step ladder, preserve protected obligations, leave actionable minimal-diff markers for reversible ceilings, and require one minimal breaking check for non-trivial logic."
---

# qtim Minimal Diff — дисциплина объёма решения

> Role-agnostic дисциплина qtim. Семантическая Codex-адаптация
> [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), MIT.

Выбирай объём решения, которое должно остаться в репозитории. Не используй skill,
чтобы сократить понимание, сузить согласованный scope, заменить поиск вариантов
или ослабить verification.

## Сначала достигни порога понимания

Перед лестницей:

1. Проследи затронутый flow и открой каждый файл, который предположительно
   изменится.
2. Назови прецеденты репозитория и задетые слои.
3. Отдели согласованные требования от спекулятивных дополнений исполнителя.

Если flow не понят, продолжай discovery. Короткая правка на неверном шве не
является минимальным решением.

## Пройди семь ступеней

Иди сверху вниз и остановись на первой ступени, которая полностью выполняет
согласованную задачу:

1. **Нужна ли новая функциональность или сущность вообще?** Убирай только
   спекулятивный каркас, future-proofing или незапрошенное расширение.
   Согласованное требование этой ступенью не сокращай.
2. **Есть ли решение в проекте?** Переиспользуй существующий helper, component,
   composable, migration pattern или принятую конвенцию.
3. **Закрывает ли standard library языка задачу?** Используй прямую штатную
   операцию без локальной обёртки, у которой нет отдельного контракта.
4. **Закрывает ли задачу платформа или фреймворк?** Предпочти native element,
   CSS, framework primitive, database constraint/index/trigger или другое
   штатное enforcement на правильном шве.
5. **Закрывает ли её уже установленная прямая зависимость?** Используй только
   объявленную dependency, уже принятую в этом слое. Не опирайся на
   транзитивный пакет. Действительно новую dependency верни architect или
   decision owner как явное решение.
6. **Хватает ли одной локальной строки или операции?** Используй её, если она
   остаётся читаемой и сохраняет границы проекта.
7. **Реализуй минимальное полноценное локальное решение.** Добавь только
   поведение согласованной задачи и её защищённые обязательства.

Если выбор не очевиден из diff, добавь одну короткую строку в уже существующий
отчёт роли: выбранная ступень, отвергнутый лишний объём и оставшийся риск.
Отдельную обязательную report schema не вводи.

## Сохрани защищённые обязательства

Не используй ступень 1 или marker, чтобы отложить или убрать:

- trust-boundary validation, включая user input, webhooks и ответы внешних API;
- обработку ошибок, предотвращающую потерю данных;
- security, authorization и разделение доступа;
- базовую accessibility: keyboard, focus и labels интерактивного UI;
- поведение, явно запрошенное пользователем;
- утверждённые acceptance criteria и документированные инварианты проекта.

Применяй ступени 2–7, чтобы найти минимальный **полноценный** способ выполнить
эти обязательства. Если согласованное требование кажется ненужным, верни его как
open question main thread или decision owner. Не закрывай урезанный scope как
Done молча.

## Помечай только осознанный обратимый потолок

Оставляй marker, только когда простое решение обратимо, находится вне protected
zones и имеет известный наблюдаемый предел:

`minimal-diff: <потолок> — <проверяемый триггер и действие>`

Пример:

`minimal-diff: линейный проход допустим до 1 000 строк — добавить индекс по scope, когда p95 превысит согласованный порог`

Считай заметку без проверяемого trigger или action некорректной. Marker не
легализует отложенную validation, security, integrity, accessibility или
approved behavior. `$qtim-team-retro` собирает markers только из доказуемого
diff текущего эпика.

## Добавь одну минимальную breaking-проверку

Для нетривиальной логики — branching, loop, parser, money, authorization или
значимый state transition — добавь одну минимальную исполняемую проверку,
которая падает при поломке поведения:

1. Предпочти существующий test runner проекта и правильный behavioral seam.
2. Если runner отсутствует, используй минимальный executable assertion.
3. Увидь красный сигнал до исправления и зелёный после.
4. Не вводи новый test framework, fixture system или suite только ради этого
   сигнала.

Этот сигнал — обязательное evidence решения, а не лишний scope. Полное coverage
и широкая regression matrix остаются отдельными testing/review gates.

## Сохрани границы с соседними disciplines

- Используй `$qtim-brainstorm`, чтобы сформировать интерпретации и design
  options; применяй лестницу после появления вариантов.
- Используй `$qtim-prototype`, чтобы разрешить рискованную design/behavior
  развилку одноразовым evidence; применяй этот skill к коду, который останется.
- Используй `$qtim-debug-loop`, чтобы воспроизвести и изолировать нетривиальный
  баг; применяй minimal-diff к root-cause fix после call-site inventory.
- Оставь main-thread orchestration, role fan-out, task ownership и persistent
  state за пределами этого skill.

## Не допускай anti-patterns

- Не проходи лестницу до понимания фактического flow.
- Не создавай абстракцию под одну реализацию без предъявленной границы: external
  port, public contract или documented invariant.
- Не добавляй новую dependency как побочный эффект реализации.
- Не ставь одинаковые patches по callers, когда поведение можно исправить на
  одном root seam.
- Не считай меньшее число файлов разрешением нарушить принятые module boundaries.
- Не делай чистую избыточность автоматическим review blocker: рекомендуй убрать
  её, но сохраняй блокирующими нарушения scope, invariant, protected zone и
  verification gate.
