from pathlib import Path


chunk_directory = Path(__file__).parent.parent
notes_path = chunk_directory / "data" / "learning_notes.txt"

notes = notes_path.read_text(encoding="utf-8")
print(notes.strip())

