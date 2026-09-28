# Personal Resilience Hub

Personal Resilience Hub is a privacy-first desktop application for organizing the information people need to stay prepared: tasks, important documents, emergency contacts, household inventory, recurring financial obligations, and emergency plans.

## Why it exists

When an unexpected event happens, important information is often scattered across notebooks, messages, spreadsheets and memory. This app brings the operational pieces into one local workspace.

## Features

- **Dashboard** with overdue, upcoming and expiring-item indicators
- **Task & reminder planning** with priority, status, due dates and recurrence
- **Document index** for IDs, insurance, warranties, leases and other important records
- **Emergency contacts** with relationship and contact details
- **Home inventory** with quantities, expiry dates, replacement cost and storage location
- **Financial obligations** with monthly/quarterly/yearly normalization
- **Emergency plans** with scenarios, instructions and meeting points
- **Global reporting** to HTML and JSON
- **Local SQLite storage** — your data stays on your computer by default
- **Automated tests** for validation and database operations
- Clean modular Python architecture

## Run

Python 3.10+ is recommended.

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Windows:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Run tests:
```bash
python -m pytest
```

## Data and privacy

The app stores its SQLite database as `resilience_hub.db` beside the application and excludes it from Git. Reports are generated only when the user requests an export.

This is an organizer and planning tool, not a substitute for professional medical, legal, financial, emergency-response or other specialist advice.

## Project structure

```
main.py
app/
  database.py
  models.py
  services.py
  reports.py
  ui.py
tests/
  test_database.py
  test_services.py
```

## Roadmap

Future releases can add encrypted backups, richer charts, OS-level notifications, attachments, import/export wizards, accessibility improvements and optional self-hosted sync.
