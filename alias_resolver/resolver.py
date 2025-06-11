# Copyright 2025 Cinvara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib
import threading
from pathlib import Path
from functools import lru_cache
import yaml

ANCHOR_FILE = "dynamics/config.yaml"


@lru_cache(maxsize=1)
def _load_config():
    """
    Search upward from the current file's directory to find the anchor config file.
    Caches the loaded config and root directory for performance.
    """
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / ANCHOR_FILE).exists():
            root = parent
            break
    else:
        raise FileNotFoundError(f"Could not locate project root via anchor: {ANCHOR_FILE}")

    with open(root / ANCHOR_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f), root


def resolve_path(alias: str) -> Path:
    """
    Resolves a file path alias defined in the config.
    """
    config, root = _load_config()
    path = config.get("paths", {}).get("aliases", {}).get(alias)
    if not path:
        available = list(config.get("paths", {}).get("aliases", {}).keys())
        raise KeyError(f"Alias '{alias}' not found. Available: {available}")
    return (root / path).resolve()


def resolve_import(name: str):
    """
    Dynamically imports and returns a function or class from a fully qualified dotted path.
    """
    config, _ = _load_config()
    dotted = config.get("imports", {}).get(name)
    if not dotted:
        available = list(config.get("imports", {}).keys())
        raise KeyError(f"Import '{name}' not found. Available: {available}")
    module, attr = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(module), attr)


def resolve_module(name: str):
    """
    Dynamically imports and returns a module by alias.
    """
    config, _ = _load_config()
    dotted = config.get("modules", {}).get(name)
    if not dotted:
        available = list(config.get("modules", {}).keys())
        raise KeyError(f"Module '{name}' not found. Available: {available}")
    return importlib.import_module(dotted)


def run_startup_tasks():
    """
    Executes background tasks specified under background_tasks.on_startup in config.
    - 'non-thread' runs immediately
    - 'threading' runs in daemon threads
    """
    config, _ = _load_config()
    startup_config = config.get("background_tasks", {}).get("on_startup", {})

    for task_name in startup_config.get("non-thread", []):
        task_fn = resolve_import(task_name)
        task_fn()

    for task_name in startup_config.get("threading", []):
        task_fn = resolve_import(task_name)
        threading.Thread(target=task_fn, daemon=True).start()


def run_shutdown_tasks():
    """
    Executes background tasks specified under background_tasks.on_shutdown in config.
    Exceptions are caught and printed.
    """
    config, _ = _load_config()
    shutdown_tasks = config.get("background_tasks", {}).get("on_shutdown", [])

    for task_name in shutdown_tasks:
        try:
            task_fn = resolve_import(task_name)
            task_fn()
        except Exception as e:
            print(f"Failed to run shutdown task '{task_name}': {e}")
