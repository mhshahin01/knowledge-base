import json
from pathlib import Path


chunk_directory = Path(__file__).parent.parent
settings_path = chunk_directory / "data" / "model_settings.json"

json_text = settings_path.read_text(encoding="utf-8")
settings = json.loads(json_text)

print(f"Model: {settings['model']}")
print(f"Temperature: {settings['temperature']}")
print(f"Streaming: {settings['stream']}")
