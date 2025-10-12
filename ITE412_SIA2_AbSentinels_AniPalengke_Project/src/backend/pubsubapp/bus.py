import os
import json
from typing import Dict, Any, List
from django.conf import settings
from threading import Lock

# Simple file-based pub/sub simulation for prototype

TOPICS_FILE = 'topics.json'
_lock = Lock()

def _topics_path():
    return os.path.join(settings.PUBSUB_DIR, TOPICS_FILE)

def _ensure_topics_file():
    os.makedirs(settings.PUBSUB_DIR, exist_ok=True)
    path = _topics_path()
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def publish(topic: str, message: Dict[str, Any]):
    _ensure_topics_file()
    with _lock:
        with open(_topics_path(), 'r', encoding='utf-8') as f:
            topics = json.load(f)
        topics.setdefault(topic, []).append(message)
        with open(_topics_path(), 'w', encoding='utf-8') as f:
            json.dump(topics, f, indent=2)

def consume(topic: str) -> List[Dict[str, Any]]:
    _ensure_topics_file()
    with _lock:
        with open(_topics_path(), 'r', encoding='utf-8') as f:
            topics = json.load(f)
        messages = topics.get(topic, [])
        topics[topic] = []
        with open(_topics_path(), 'w', encoding='utf-8') as f:
            json.dump(topics, f, indent=2)
        return messages
