import json
import os
from typing import Any, Dict, List
from django.conf import settings
from threading import Lock

_file_locks: Dict[str, Lock] = {}

def _get_lock(path: str) -> Lock:
    if path not in _file_locks:
        _file_locks[path] = Lock()
    return _file_locks[path]

def _ensure_file(path: str, default: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=2)

def read_json(name: str, default: Any) -> Any:
    path = os.path.join(settings.DATA_DIR, name)
    _ensure_file(path, default)
    with _get_lock(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

def write_json(name: str, data: Any) -> None:
    path = os.path.join(settings.DATA_DIR, name)
    _ensure_file(path, data)
    with _get_lock(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
