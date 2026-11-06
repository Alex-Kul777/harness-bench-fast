# add-fork-fail-output — design

## Замороженная логика

### 1. Нормализация per-task записи
В функции нормализации `results[]` (около строки 221) добавить поле:
`"error": "" if entry.get("error") is None else str(entry.get("error"))`.

### 2. `task_reason(message, error)` — короткий текст для `Note`
```
def task_reason(message, error):
    if error: return error                      # напр. "timed out after 3600s"
    m = (message or "").strip()
    if not m.startswith("{"): return trunc(m)    # прозаический message
    try: obj = json.loads(m)
    except Exception: return trunc(m)
    if isinstance(obj, dict) and len(obj) == 1:  # {"wave19": {...}} -> {...}
        only = next(iter(obj.values()))
        if isinstance(only, dict): obj = only
    if isinstance(obj, dict):
        if isinstance(obj.get("reason"), str) and obj["reason"].strip():
            return obj["reason"]
        bits = [f"{k}={obj[k]}" for k in
                ("decision_correct","response_correct","invalid_calls","extra_requests","status","submission_count")
                if k in obj]
        if bits: return ", ".join(bits)
    return trunc(m)
```
`trunc(s)` = s, если len<=120, иначе s[:119] + "…".

### 3. Рендер `Note` в Tasks-таблице
- Ячейка `Note` = `_esc(task_reason(message, error))`.
- Дополнительно, **если** `error` непусто **или** `message.strip().startswith("{")`,
  добавить внутрь той же ячейки:
  `<details class="task-detail"><summary>output</summary><pre>…</pre>[<p>error: …</p>]</details>`
  - `<pre>` = pretty JSON (`json.dumps(obj, ensure_ascii=False, indent=2)`) при успешном
    парсинге, иначе escaped message; **всё** через `html.escape`.
  - `<p>error: …</p>` — только если `error` непусто.
- В `<head>` страницы детализации добавить короткий `<style>`:
  `.task-detail pre{max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word}`.

### 4. Совместимость
- Колонки/секции не меняются; escaping обязателен; `--check` (JSON) не зависит от этого.

## Верификация
- Регенерация: `docs/fork-run-<id>.html` содержит `task-detail` для упавших задач;
  для `task_456_build_critical_path` видно `timed out after 3600s`.
- Инъекционный тест: сообщение с `<script>` рендерится экранированным.
