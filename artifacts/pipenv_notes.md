Great! Here’s a **simple checklist + script snippet** you can follow to reliably activate your Pipenv environment and run your ETL script without confusion:

---

# 🔥 Reliable way to run your ETL script with Pipenv

### Step 1: Check if `pipenv` is installed globally

Run in terminal:

```bash
pipenv --version
```

* If you get “command not found”, install it globally:

```bash
brew install pipenv
```

---

### Step 2: Activate Pipenv shell (only once per terminal)

```bash
pipenv shell
```

* If you see a message about “already activated, avoiding nested environment”, it means you are already in pipenv shell.
* If you don’t want to enter shell, use **step 4** below instead.

---

### Step 3: Run your ETL script inside the shell

```bash
python data_ingestion.py
```

---

### Step 4: Run your ETL script without activating shell (recommended)

This runs your script directly in the Pipenv-managed environment without needing to activate a shell:

```bash
pipenv run python data_ingestion.py
```

---

### Optional: Step 5 — Run Python from the virtualenv directly

Find your pipenv virtualenv path:

```bash
pipenv --venv
```

Output example:

```
/Users/sudhirjoon/.local/share/virtualenvs/REST_Countries_ETL_to_PostgreSQL-sYyv6i3o
```

Run your script explicitly with that Python interpreter:

```bash
/Users/sudhirjoon/.local/share/virtualenvs/REST_Countries_ETL_to_PostgreSQL-sYyv6i3o/bin/python data_ingestion.py
```

---

### Bonus: Minimal example for `data_ingestion.py` to test `dotenv`

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file from current directory

print("API_URL =", os.getenv("API_URL"))
```

Make sure your `.env` file is in the same folder and contains:

```
API_URL=https://restcountries.com/v3.1/all
```

---

# TL;DR

* Use `pipenv run python data_ingestion.py` to avoid environment confusion
* Ensure `pipenv` is installed globally so you can run commands easily
* Keep your `.env` file in the project root and load it with `load_dotenv()`

---

If you want, I can help you automate this in a bash script or a Makefile to make your workflow even smoother!
