# Smart BI Assistant

A natural-language interface to a business database. You type a question like
*"which products bring in the most revenue?"* and it writes the SQL, runs it, and
shows you the answer as a table and a chart — no SQL knowledge needed.

I built it as a personal project to see how far natural-language-to-SQL could go.
Under the hood it uses a language model to turn plain English into SQL, running
against the Northwind sample database.

**Live demo:** https://smart-bi-assistant-xnr5vq24a86rt97nzwxaud.streamlit.app/

## What you can do with it

- Ask questions in English instead of writing queries by hand
- See the exact SQL it generated, and edit it yourself if it got something wrong
- Browse results as a table, download them as CSV, or switch to a chart
- Start from a set of example questions if you're not sure what to ask

## Screenshots

Ask a question in plain English:

![Home](docs/home.png)

Results come back as a table with a few quick stats and a CSV download:

![Results](docs/results.png)

The generated SQL is always shown, and you can edit and re-run it:

![SQL editor](docs/sql-editor.png)

## Running it locally

You'll need Python and a free Hugging Face token — the app calls a model through
Hugging Face's API to generate the SQL.

Clone the repo and install the dependencies:

```bash
git clone https://github.com/houas-sarah/smart-bi-assistant.git
cd smart-bi-assistant
pip install -r requirements.txt
```

Get a token from https://huggingface.co/settings/tokens and put it in a `.env`
file in the project folder:

```
HF_API_KEY=hf_your_token_here
HF_MODEL_NAME=Qwen/Qwen2.5-Coder-32B-Instruct
```

Then run it:

```bash
streamlit run app.py
```

It opens at http://localhost:8501. The model name is optional — leave it out and
it falls back to the Qwen coder model above.

## About the database

It ships with an expanded version of Northwind, the classic sample database for a
small import/export company. This version is much bigger than the original so
that trends and aggregations are actually interesting to query — around 16,000
orders and 600,000 order lines, across 93 customers and 77 products, dated
2012 to 2023.

The data is synthetic, so don't read too much into the revenue figures. A single
"customer" pulling in millions is just an artifact of how the data was generated.

## How it works

The pipeline is short:

```
your question  →  model writes SQL  →  SQL runs on SQLite  →  table + chart
```

A few guardrails keep it safe and honest:

- **The SQL is parsed, not string-matched.** Every query is parsed into a syntax
  tree with [`sqlglot`](https://github.com/tobymao/sqlglot). Only a single
  read-only statement (`SELECT` / `WITH`) is allowed; anything that writes,
  changes the schema, chains multiple statements, or can't be parsed is rejected.
  This is far harder to fool than keyword blocking — and it doesn't wrongly reject
  a valid query just because a word like `delete` appears inside a text value.
- **The connection is read-only.** Queries run over a SQLite connection opened in
  `mode=ro`, so even a query that somehow slipped past validation physically
  cannot modify the data.
- **The SQL is always visible and editable.** A language model can misread a
  question, so you can open the SQL tab, fix the query, and run your edited
  version — it goes through exactly the same checks.

## Is the SQL always correct?

Safety, yes — it can't modify anything. Correctness, not always. The queries are
written by a language model, so it can misunderstand a question or join the wrong
tables now and then. That's the reason the app shows you the query and lets you
edit it: think of it as a fast first draft to check, not a guaranteed answer.

## Tests

There's a small offline test suite (no API key or network needed) that covers the
query validation and the SQL-cleaning logic:

```bash
pip install -r requirements-dev.txt
pytest
```

## Things I'd add next

- Feed query errors back to the model so it can fix its own mistakes
- Support databases other than the bundled Northwind file
- Cache repeated questions
- Let the model pick the most fitting chart type for each result

## License

MIT — see the [LICENSE](LICENSE) file.
