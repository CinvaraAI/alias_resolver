# 🔗 Alias Resolver for Python Projects

A lightweight utility to centralize and dynamically resolve **file paths**, **module imports**, and **startup/shutdown tasks** in Python using a YAML config file.

---

## 🚀 Features

- 📁 Project-relative file path resolution (`resolve_path`)
- 📦 Dynamic function/class/module import (`resolve_import`, `resolve_module`)
- 🔁 FastAPI-friendly startup/shutdown task execution
- ⚙️ Config-driven — zero hardcoded paths or strings
- 🧠 Auto-locates your project root using a known anchor (e.g. `dynamics/config.yaml`)

---

## 📂 Example Project Structure

alias-resolver/
├── resolver.py
├── main.py
├── dynamics/
│ └── config.yaml
├── src/
│ └── log_writer.py

---

## 🛠️ Quick Start

### 1. Define Aliases in `dynamics/config.yaml`

```yaml
paths:
  aliases:
    log_writer: src/log_writer.py
    data_file: data/input.json

imports:
  write_log: src.log_writer.write_log
  warmup_cache: src.services.cache.warmup
  close_connection: src.services.db.shutdown

modules:
  logger: src.log_writer

background_tasks:
  on_startup:
    non-thread:
      - warmup_cache
    threading:
      - some_background_job
  on_shutdown:
    - close_connection

### 2. Use in Your Code

from resolver import resolve_path, resolve_import, resolve_module

# Resolve a file path
log_file_path = resolve_path("log_writer")

# Resolve a function
write_log = resolve_import("write_log")
write_log("App started.")

# Resolve a module
logger = resolve_module("logger")
logger.write_log("Logging via module")

### 3. Handle Lifecycle Events (FastAPI)

from fastapi import FastAPI
from resolver import run_startup_tasks, run_shutdown_tasks

app = FastAPI()

@app.on_event("startup")
def startup():
    run_startup_tasks()

@app.on_event("shutdown")
def shutdown():
    run_shutdown_tasks()

🔐 License

Licensed under the Apache License 2.0 — free to use, modify, and share.

🧱 Future Ideas

CLI to list/resolve aliases

pyproject.toml or setup.py for pip install

Optional validation of config file

✨ Author
CinvaraAI
