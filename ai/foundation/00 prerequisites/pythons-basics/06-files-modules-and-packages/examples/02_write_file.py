from pathlib import Path


chunk_directory = Path(__file__).parent.parent
output_directory = chunk_directory / "output"
output_directory.mkdir(exist_ok=True)

summary_path = output_directory / "study_summary.txt"
summary_path.write_text("Completed Chunk 06.\n", encoding="utf-8")

print(f"Saved: {summary_path.name}")

