# Domain docs

## Layout

**Single-context.** One glossary and one ADR directory at the repo root:

- `GLOSSARY.md` — the benchmark domain vocabulary (shot list, discrimination
  power, wave, stable failure, coverage/speed trade-off).
- `docs/adr/` — architecture decision records, `NNNN-kebab-title.md`.

## Consumers

`domain-modeling` and `grill-with-docs` read `GLOSSARY.md` and write ADRs inline;
`grill-me` is the stateless variant. Keep vocabulary in `GLOSSARY.md` only; do
not duplicate it in other docs.
