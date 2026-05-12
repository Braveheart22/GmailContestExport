# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Does

Single-purpose Python script that exports 2026 Gift Contest entries from Gmail to a date-stamped Excel file and emails the result to Maryellen@LoopLoc.com. Designed to run as a Windows scheduled task via `run_export.bat`.

## Running the Export

```bat
run_export.bat
```

This runs `export_contest_entries.py` via the full Python path (`C:\Users\John.LOOP\AppData\Local\Programs\Python\Python314\python.exe`) and appends output to `export_log.txt`.

To run the script directly:

```bat
C:\Users\John.LOOP\AppData\Local\Programs\Python\Python314\python.exe export_contest_entries.py
```

## Authentication

- `credentials.json` — Google OAuth client secret (gitignored, must be present)
- `token.pickle` — Saved OAuth token (gitignored, auto-created on first run)

On first run (or if the token is missing/expired), a browser window opens for Google login. After that, `token.pickle` caches the credentials so subsequent runs are non-interactive.

Required Gmail scopes: `gmail.readonly` + `gmail.send`

## Utility Scripts

| Script | Purpose |
|---|---|
| `test_gmail.py` | Verify Gmail connection and print account info |
| `list_labels.py` | List all Gmail labels and their IDs (useful if the label ID changes) |
| `list_contest_emails.py` | Browse the first 10 emails under the contest label |
| `read_first_email.py` | Print the raw body of the first contest email |

## Key Constants (in `export_contest_entries.py`)

- `LABEL_ID` — Gmail label ID for the contest inbox (`Label_6083117079229242213`)
- `BACKUP_RECIPIENT` — Email address that receives the daily xlsx (`Maryellen@LoopLoc.com`)
- `OUTPUT_FILE` — Date-stamped output filename (`2026_Gift_Contest_YYYY-MM-DD.xlsx`)

## Email Parsing

Contest entries arrive as HTML emails. Fields are extracted with `re.search` against the decoded HTML body using patterns like `r"First Name:\s*</b>(.*?)<"`. If a field isn't matched, it stores an empty string — no exception is raised.

The script handles both direct-body emails and multipart emails (checks `text/plain` then `text/html`).
