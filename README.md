# 📊 Smart BI Assistant

> Ask business questions in plain English and get instant answers with SQL, tables, and charts.

Smart BI Assistant is a natural-language business-intelligence tool. You type a
question like *"Who are my top 5 customers by revenue?"*, an online LLM converts
it into a safe SQL query, and the app runs it against a demo business database and
shows the results as an interactive table and chart — with one-click CSV export.

Built with **Streamlit**, the **Hugging Face Inference API**, and the classic
**Northwind** sample database.

---

## ✨ Features

- 💬 **Natural language → SQL** — powered by an online LLM (no local model needed)
- 🔒 **Read-only & validated** — only `SELECT`/`WITH` queries are allowed; destructive statements are blocked
- ✏️ **Human-in-the-loop** — inspect, edit, and re-run the generated SQL so you can verify the AI's work
- 📊 **Auto visualizations** — tables plus automatic bar charts for numeric results
- ⬇️ **CSV export** — download any result set
- 🕘 **Query history** — recent questions kept in the sidebar
- 🎨 **Modern dark UI** — custom-themed Streamlit interface

---

## 🖼️ How it works

```
Your question  ──►  LLM (Hugging Face)  ──►  SQL query  ──►  SQLite (Northwind)  ──►  Table + Chart
```

---

## 📸 Screenshots

**Ask a question in plain English**

![Home](docs/home.png)

**Get results as a table — with row/column/timing metrics and CSV export**

![Results](docs/results.png)

**Inspect, edit, and re-run the generated SQL (human-in-the-loop)**

![SQL editor](docs/sql-editor.png)

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smart-bi-assistant.git
cd smart-bi-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

The app uses the Hugging Face Inference API to generate SQL, so a free token is
**required**.

1. Get a free token at <https://huggingface.co/settings/tokens>
2. Copy the example environment file and fill in your token:

```bash
cp .env.example .env
```

```env
HF_API_KEY=hf_your_token_here
HF_MODEL_NAME=Qwen/Qwen2.5-Coder-32B-Instruct
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

Then open your browser at <http://localhost:8501>.

---

## ☁️ Deployment (Streamlit Community Cloud)

The app deploys for free straight from GitHub — no server setup required.

1. Push this repository to GitHub.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub** and select:
   - **Repository:** `your-username/smart-bi-assistant`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Open **Advanced settings → Secrets** and paste your credentials in TOML form:

   ```toml
   HF_API_KEY = "hf_your_token_here"
   HF_MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"
   ```

5. Click **Deploy**. The first build installs `requirements.txt`; after that the
   app is live at a public `*.streamlit.app` URL.

> **Notes**
> - The `HF_API_KEY` is read from Secrets, never from the repo.
> - By default the deployed URL is public. Restrict access under
>   **Settings → Sharing** if needed, and consider rotating your token after testing.

---

## 💡 Example Questions

- How many customers are there?
- List the top 10 customers by total revenue.
- Which countries have the most customers?
- What are the top 5 best selling products?
- Show me the total sales per country.
- Which employees have generated the most revenue?
- Which products are low in stock?
- Show monthly sales totals.

---

## 🗄️ Database

Uses an expanded version of the well-known **Northwind** trading-company
database (`northwind.db`, SQLite), which models an import/export business. This
build is scaled up from the classic sample so that trend and aggregation queries
return meaningful results:

| Data | Count |
|------|-------|
| Orders | 16,282 |
| Order line items | 609,283 |
| Customers | 93 |
| Products | 77 |
| Employees | 9 |
| Date range | 2012 – 2023 |

Tables include `Customers`, `Orders`, `Order Details`, `Products`, `Categories`,
`Employees`, `Suppliers`, `Shippers`, and more. The values are **synthetic demo
data**, not real business figures.

---

## 📁 Project Structure

```
smart-bi-assistant/
├── app.py                 # Streamlit UI
├── query_engine.py        # Text-to-SQL engine (Hugging Face Inference API)
├── database.py            # Safe, read-only SQLite query execution
├── northwind.db           # Northwind demo database (SQLite)
├── tests/                 # Offline unit tests (pytest)
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Dev/test dependencies
├── .env.example           # Environment variable template
└── README.md
```

---

## ⚙️ Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_API_KEY` | ✅ Yes | — | Your Hugging Face access token |
| `HF_MODEL_NAME` | No | `Qwen/Qwen2.5-Coder-32B-Instruct` | Any chat model on the HF router |

---

## 🔐 Security

- Only `SELECT` / `WITH` queries are executed; `DROP`, `DELETE`, `INSERT`,
  `UPDATE`, `ALTER`, `CREATE`, and `TRUNCATE` are rejected.
- Generated SQL is cleaned and validated before it touches the database.
- Secrets are read from environment variables and never committed.

---

## 🎯 How accurate is it?

There are two separate questions here, and it's worth being precise:

- **Safety is guaranteed.** Every query — whether generated by the AI or edited by
  hand — passes read-only validation. Only `SELECT` / `WITH` statements run;
  anything that could modify data is rejected. The worst case is a query that
  returns nothing.
- **Semantic correctness is _not_ guaranteed.** The SQL is written by a language
  model, which can misinterpret a question or join the wrong tables. To keep the
  tool trustworthy, the app is built around **human verification** rather than
  blind trust:
  - The generated SQL is always shown.
  - You can **edit the query and re-run it** (SQL tab → *Verify & re-run*), so the
    AI drafts and a human confirms.
  - A low sampling temperature and a code-specialised model make output stable.

In short: treat it as a fast first draft that you can inspect and correct — not as
an infallible oracle.

---

## 🧪 Testing

The project ships with an offline test suite (no API key or network needed) that
covers SQL validation, query execution, and the text-to-SQL cleaning/parsing
helpers.

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## ⚠️ Limitations & Future Work

**Current limitations**

- **LLM dependence** — SQL quality depends on the chosen model; complex or
  ambiguous questions can produce incorrect (though always read-only) queries.
- **No automatic self-correction** — if a generated query errors, the app reports
  it and lets you fix the SQL by hand, rather than retrying automatically with the
  error as feedback.
- **Single database** — the schema and connection are hard-wired to the bundled
  Northwind SQLite file.
- **Synthetic data** — figures are demo values, not real business data.
- **Online model required** — generation calls the Hugging Face Inference API, so
  an internet connection and a valid token are required.

**Future work**

- Feed database errors back to the LLM for automatic query repair.
- Add result caching for repeated questions.
- Support additional databases (PostgreSQL/MySQL) and schema switching.
- Let the LLM suggest the most appropriate chart type per result.
- Add user authentication and per-user query history.

---

## 🧑‍💻 Author

**Sarah Houas** — Master's Thesis Project, ESTIN 2025
📧 s_houas@estin.dz

## 📄 License

Released under the [MIT License](LICENSE).
