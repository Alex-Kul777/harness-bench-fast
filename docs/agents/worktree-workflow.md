# Worktree workflow: работа с HBF из нескольких сессий OpenClaw

> Как одному агенту (и человеку) работать с одним репозиторием
> `harness-bench-fast` в нескольких параллельных сессиях, не мешая друг другу.

## Зачем это нужно

Репозиторий HBF нужен одновременно во многих задачах: прогоны моделей, фиксы
раннеров, новые волны, документация, правки форков. Если все сессии работают в
**одном** рабочем каталоге, они мешают друг другу: переключение веток, «грязный»
checkout, конфликтующие правки, потеря незакоммиченного.

Решение — **git worktree**: один объектный стор `.git`, много рабочих каталогов,
каждый на своей ветке. OpenClaw умеет управлять такими чекаутами сам
(**managed worktree**) — это тот же git-worktree плюс регистрация, снапшоты,
очистка и лимиты.

## Два уровня «worktree»

| | Git worktree | OpenClaw managed worktree |
|---|---|---|
| Кто создаёт | вы вручную (`git worktree add`) | OpenClaw при создании сессии / спавна |
| Жизненный цикл | вы удаляете сами | авто-снапшот + авто-очистка + эвикция |
| Регистрация | нет | state-БД OpenClaw, привязка к сессии (`sessionRoot`) |
| Где лежит | где укажете (`/tmp/...`) | под `worktreeRoot` |
| Политики | от шелла | tool/exec-политика сессии, sandbox `cwd` |
| Ускорение ФС | нет | Btrfs / APFS / ReFS снапшоты |
| Суть | «сырой» VCS-механизм | **git worktree + оркестрация OpenClaw** |

Ключевое: managed worktree — это **надстройка** над обычным git-worktree, а не
альтернатива ему.

## Правила именно для этого репозитория

- **Общий чекаут** (тот, что клонирован на диске):
  `/home/kap/.openclaw/workspace/projects/benchmark-research/harness-bench-fast`.
  В нём **никогда не переключать ветку** и не делать коммиты «в общий» — он должен
  оставаться стабильным для всех сессий.
- **Remotes**:
  - `origin` → `git@github.com:Alex-Kul777/harness-bench-fast.git` — наш форк,
    пушим сюда;
  - `upstream` → `git@github.com:ai-forever/harness-bench-fast.git` — только
    `fetch` для подтягивания апстрима.
- **Ветвиться всегда от `origin/main`** (или явного base ref).
- **Коммить рабочее.** Незакоммиченные/untracked файлы в managed worktree могут
  быть удалены эвикцией (см. лимиты ниже).
- Одна задача = одна ветка = один worktree.

## Рецепт A — OpenClaw-native (рекомендуется)

Каждая сессия/подзадача получает **свою** ветку и чекаут над общим `.git`.

- **Через UI:** New Session → выбрать существующую папку Gateway с путём к HBF
  (или зарегистрированный проект).
- **Через спавн/сессию:** `worktree: true` + `cwd` = путь к репо, либо
  `projectId`/`projectGitUrl` для другого репозитория.

Пример параметров спавна:

```json
{
  "task": "fix runner X",
  "runtime": "subagent",
  "worktree": true,
  "worktreeName": "runner-x-fix",
  "worktreeBaseRef": "origin/main",
  "cwd": "/home/kap/.openclaw/workspace/projects/benchmark-research/harness-bench-fast"
}
```

Примечания:

- `worktree: true` без `cwd`/`projectId`/`projectGitUrl` наследует живой managed
  репозиторий родителя.
- Скрытые сабагенты могут запросить managed worktree (`worktree: true`) и без
  сайдбар-сессии; `worktreeName` и `worktreeBaseRef` требуют
  `runtime: "subagent"`.
- `cleanup: "delete"` — после завершения снапшотит и удаляет чекаут;
  `cleanup: "keep"` — оставляет.
- ACP **не** поддерживает managed worktree.

## Рецепт B — ручной git worktree (быстрые правки)

```bash
cd /home/kap/.openclaw/workspace/projects/benchmark-research/harness-bench-fast

# 1. отдельный чекаут на своей ветке от main
git worktree add /tmp/hbf-<task> -b <branch> origin/main

# 2. правки и коммиты — ВНУТРИ этого каталога
cd /tmp/hbf-<task>
# ... edit / commit ...

# 3. посадка ветки на main (см. ниже), затем уборка
git worktree remove /tmp/hbf-<task> --force
```

## Рецепт C — параллельные правки скрытыми сабагентами

То же, что B, но работу делегирует агент: сабагенет (или несколько) правят в
изолированном worktree, родитель проверяет результат «на шве», затем ветку сажают
на `main` через тот же ff-merge. См. скилл `parallel-subagent-small-edits`.

## Посадка ветки на main

```bash
# в ветке/чекауте, собранном от origin/main
git fetch origin

git merge --ff-only <branch>     # main не разошёлся → fast-forward
git push origin HEAD:main

# если main успел разойтись:
git rebase origin/main           # переставить свою ветку поверх
# снова: git merge --ff-only / git push origin HEAD:main
```

Альтернатива — обычный Pull Request в `origin` (форк).

## Лимиты и подводные камни (OpenClaw)

- `worktreeMaxCount` (по умолчанию **4096**) — общий лимит живых managed worktree
  на все агенты/репозитории в одном state-dir. При переполнении идёт эвикция:
  сначала merged/squashed, затем по давности — **включая незакоммиченное**.
  Нужное сохраняйте в коммитах/снапшотах.
- `worktreeRoot` — где OpenClaw кладёт чекауты (по умолчанию
  `<state-dir>/worktrees`); снаружи этого корня cleanup трогает только
  зарегистрированные worktree.
- `worktreeAcceleration` — ускорение создания через снапшоты ФС
  (Btrfs/APFS/ReFS); `false` отключает.
- `sessionRoot` = чекаут worktree → это граница ФС и точка применения
  tool/exec-политики сессии.
- Linked worktree'ы одного репозитория делят **project identity** (тёплые образы,
  Git-seed → быстрее старт).

## Ссылки

- OpenClaw: `docs/concepts/managed-worktrees.md`, `docs/gateway/config-runtime.md`
  (`worktreeRoot` / `worktreeAcceleration` / `worktreeMaxCount`),
  `docs/tools/subagents/tool-reference.md` (параметр `worktree`).
- Скиллы: `.agents/skills/harness-bench-fast/SKILL.md`,
  `parallel-subagent-small-edits` (workshop).
- Удалённые/облачные сессии: `docs/gateway/cloud-sessions.md`
  (Gateway-source managed worktree).
