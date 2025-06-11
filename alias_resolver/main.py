from resolver import resolve_path, resolve_import, resolve_module, run_startup_tasks, run_shutdown_tasks

from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def startup():
    run_startup_tasks()

@app.on_event("shutdown")
def shutdown():
    run_shutdown_tasks()

@app.get("/")
def index():
    write_log = resolve_import("write_log")
    write_log("Handling request to /")

    log_path = resolve_path("log_writer")
    return {"message": "Hello, world!", "log_path": str(log_path)}
