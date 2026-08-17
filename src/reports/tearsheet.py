from pathlib import Path

def list_tearsheets(out_dir):
    return sorted(Path(out_dir).glob("*_tearsheet.pdf"))
