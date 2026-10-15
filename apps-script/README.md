# FreePPTMaker website setup

The website (`docs/`) runs on **GitHub Pages**. The AI calls go through a **Google Apps Script** web app, so your API keys stay secret.

```
Browser (GitHub Pages)  ──►  Google Apps Script  ──►  Groq / Gemini / Mistral
  builds the .pptx           holds the API keys
```

## 1. Create the Apps Script backend (about 5 minutes)

1. Open <https://script.google.com> and click **New project**.
2. Delete the sample code, paste in all of `apps-script/Code.gs`, and save.
3. Open **Project Settings** (⚙️) → **Script properties** → **Add script property**. Add at least one key:
   | Property | Where to get it (free tier available) |
   |---|---|
   | `GROQ_API_KEY` | <https://console.groq.com/keys> |
   | `GEMINI_API_KEY` | <https://aistudio.google.com/apikey> |
   | `MISTRAL_API_KEY` | <https://console.mistral.ai/api-keys> |

   If you add more than one key, the script tries the next provider when one fails.
4. Back in the editor, choose the `testSetup` function and click **Run**. Allow the permissions. The log should show a JSON reply.
5. Click **Deploy** → **New deployment** → type **Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
   
   Click **Deploy** and copy the **Web app URL** (it ends with `/exec`).

## 2. Connect the website

Open `docs/js/config.js` and paste the URL:

```js
APPS_SCRIPT_URL: 'https://script.google.com/macros/s/XXXXXXXX/exec',
```

## 3. Publish on GitHub Pages

1. Commit and push the `docs/` folder to GitHub.
2. In the repo, open **Settings** → **Pages** → Source: **Deploy from a branch** → Branch: `main`, folder: `/docs` → **Save**.
3. After a minute or two the site is live at `https://<username>.github.io/FreePPTMaker/`.

## Updating the Apps Script later

With clasp (this folder is already linked to the project):

```
cd apps-script
clasp -u personal push
clasp -u personal update-deployment AKfycbyidlz87-ZZFSK5j2cytmNuxeR0pyMPtyaPrCFsYgL2gnPUiFFgEi2pPtKGftZV6EYC
```

Or by hand in the editor: after you change `Code.gs`, open **Deploy** → **Manage deployments** → ✏️ → Version: **New version** → **Deploy**. This keeps the same URL. If you create a *new* deployment instead, you get a new URL that you would have to paste into `config.js` again.

## Optional settings (Script properties)

| Property | Default | Use |
|---|---|---|
| `PROVIDER_ORDER` | `groq,gemini,mistral` | Which provider is tried first |
| `GROQ_MODEL` | picked automatically | Force a specific Groq model |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Force a specific Gemini model |
| `MISTRAL_MODEL` | `mistral-small-latest` | |
| `MAX_REQUESTS_PER_MINUTE` | `30` | Basic protection against abuse |

If a provider retires a model, the script looks up a current one, saves it as `AUTO_GROQ_MODEL` / `AUTO_GEMINI_MODEL`, and carries on.

## Testing locally

From the repo folder, run `python -m http.server 8000 --directory docs` and open <http://localhost:8000>. Don't open `index.html` directly by double-clicking it.
