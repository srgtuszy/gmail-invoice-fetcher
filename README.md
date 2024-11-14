# Gmail Invoice Fetcher 📧 → 📂

Born out of the monthly panic of "where the hell are all my invoices?" when tax season hits. If you're like me and your inbox is a black hole of PDFs, this script is your rescue mission.

## What It Does

- 🔍 Searches your Gmail for emails with attachments
- 📄 Reads the content of PDF attachments
- ⬇️ Downloads only PDFs containing specific text (like "invoice", "facture", or your company's tax ID)
- 📅 Filters by date range (so you can fetch just what you need for tax season)

## Setup (I Promise It's Quick)

1. Clone the repo: 
2. Install the stuff it needs:

```bash
pip install -r requirements.txt
```

3. Get your Google credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Make a new project (name it whatever)
   - Enable Gmail API
   - Create OAuth credentials (Desktop app)
   - Download and rename to `credentials.json` in the project folder

## How to Use It

1. Set up what you're looking for:

The important bit - what text to look for in PDFs

```bash
export SEARCH_STRINGS="<insert VAT number>,<insert company name>"
export START_DATE="2024/01/01"
export END_DATE="2024/12/31"
```

2. Run it:

```bash
./fetch_invoices.py
```

3. First time? It'll open your browser for Google login. After that, it remembers you.

4. Grab a coffee ☕️ while it:
   - Digs through your emails
   - Reads all the PDFs
   - Saves the ones that match your search

5. Check the `attachments/` folder for your invoices!
