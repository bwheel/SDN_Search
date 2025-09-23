# SDN Search Web App

A client-side searchable web app for the [US Treasury OFAC SDN List](https://sanctionslist.ofac.treas.gov/Home/SdnList), powered by SQLite and SQL.js. The project supports fast full-text search using FTS5 in the browser and using Bootstrap 5.

---

## Features

- Search SDN entries by name, program, title, vessel, and owner.
- Full-text search powered by SQLite FTS5 in the browser (via SQL.js).
- Mobile-friendly and responsive UI with Bootstrap 5.
- Prebuilt SQLite database for fast client-side searching.
- Simple development workflow using `uv`.

---

## building the db
``` bash
uv run python -m scripts.create_db
```

## running the dev server locally
``` bash
uv run python -m scripts.dev_server
```
