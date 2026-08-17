from pathlib import Path

def list_sector_reports(out_dir):
    return sorted(Path(out_dir).glob("*_report.pdf"))
