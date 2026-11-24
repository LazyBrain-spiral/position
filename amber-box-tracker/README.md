# Amber Box Tracker

Tracks delivered cartons from the gate to the right shelf, alerts on wrong floor, wrong shelf and
missing cartons, and answers site questions through Amber, a short-answer assistant.

> Draft. Sections marked TODO are filled when the other tracks land.

## Setup (Windows and macOS)
TODO: Python 3.11, virtualenv, `pip install -r requirements.txt`, `python scripts/setup.py`.

## Amber assistant
Amber answers in one or two spoken sentences and always uses tools, never guessed locations.

| Tool | Purpose |
| :-- | :-- |
| `find_carton` | Fuzzy search by label code, part number, name or PO. `auto_locate` lights the shelf. |
| `where_does_this_go` | Destination floor and shelf of a carton. |
| `delivery_status` | Expected, seen and missing cartons of a delivery. |
| `report_damage` | Two steps: asks to confirm, then records the damage and an alert. |
| `list_open_alerts` | Summary of open alerts. |

Provider choice is automatic: `ANTHROPIC_API_KEY` uses Claude, `GEMINI_API_KEY` uses Gemini, and
with neither set (or the SDK missing) the offline regex provider runs with no network.
Keys live in `.env`, never in code.

Offline phrases: `where is <x>`, `find <x>`, `light up <x>`, `blink <x>`, `show <x>`,
`where does <code> go`, `status of DEL-2211`, `<code> is damaged: <note>`, `open alerts`.

Damage needs confirmation. The chat call returns `needs_confirmation: true`; send the same
message again with `confirm: true` to record it. The model can never confirm for itself.

## Tests
`pytest tests/test_amber.py` (no network, no API keys).

## TODO
HTTPS certificate guide for `/m`, recording guide, 3-minute demo script, licence notes
(AGPL for RF-DETR/YOLO weights, Meta glasses acceptable-use), troubleshooting, deviations.
