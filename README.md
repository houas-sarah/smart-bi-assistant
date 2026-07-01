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
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

Then open your browser at <http://localhost:8501>.

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

Uses the classic **Northwind** trading-company database (`northwind.db`, SQLite),
which models a small import/export business:

| Data | Approx. count |
|------|---------------|
| Orders | 830 |
| Customers | 91 |
| Products | 77 |
| Employees | 9 |

Tables include `Customers`, `Orders`, `Order Details`, `Products`, `Categories`,
`Employees`, `Suppliers`, `Shippers`, and more.

---

## 📁 Project Structure

```
smart-bi-assistant/
├── app.py              # Streamlit UI
├── query_engine.py     # Text-to-SQL engine (Hugging Face Inference API)
├── database.py         # Safe, read-only SQLite query execution
├── northwind.db        # Northwind demo database (SQLite)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md
```

---

## ⚙️ Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_API_KEY` | ✅ Yes | — | Your Hugging Face access token |
| `HF_MODEL_NAME` | No | `mistralai/Mistral-7B-Instruct-v0.2` | Any text-generation model on the HF router |

---

## 🔐 Security

- Only `SELECT` / `WITH` queries are executed; `DROP`, `DELETE`, `INSERT`,
  `UPDATE`, `ALTER`, `CREATE`, and `TRUNCATE` are rejected.
- Generated SQL is cleaned and validated before it touches the database.
- Secrets are read from environment variables and never committed.

---

## 🧑‍💻 Author

**Sarah Houas** — Master's Thesis Project, ESTIN 2025
📧 s_houas@estin.dz

## 📄 License

Released under the [MIT License](LICENSE).
