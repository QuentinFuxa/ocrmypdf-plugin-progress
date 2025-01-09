from ocrmypdf import ocr, hookimpl
from ocrmypdf.pluginspec import ProgressBar
from pathlib import Path

_ocr_progress = {}

def do_ocr_in_background(input_pdf_path: Path, output_pdf_path: Path) -> None:
    """
    Perform OCR in the background using ocrmypdf, updating progress along the way.
    Clears the progress at both start and end, and sets 'terminated' state when done.
    """
    try:
        clear_ocr_progress()
        ocr(
            str(input_pdf_path),
            str(output_pdf_path),
            force_ocr=True,
            progress_bar=True,
            plugins=["ocr_functions"],
        )
    except Exception as exc:
        raise Exception("Error running ocrmypdf in background.")
    finally:
        clear_ocr_progress()
        set_ocr_progress("terminated", True)

def set_ocr_progress(key, value):
    _ocr_progress[key] = value

def get_ocr_progress():
    return _ocr_progress

def clear_ocr_progress():
    _ocr_progress.clear()

class MyProgressBar(ProgressBar):
    def __init__(
        self,
        total: int | None,
        desc: str | None,
        unit: str | None,
        disable: bool = False,
    ):
        self.progress_bar = 0
        clear_ocr_progress()
        set_ocr_progress("total", total)
        set_ocr_progress("desc", desc)
        set_ocr_progress("unit", unit)
        set_ocr_progress("progress_bar", self.progress_bar)
        print(get_ocr_progress())

    def update(self, n=1, completed=None):
        
        if completed:
            self.progress_bar = completed
        else:
            self.progress_bar += n
        set_ocr_progress("progress_bar", self.progress_bar)
        print(get_ocr_progress())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

@hookimpl
def get_progressbar_class():
    return MyProgressBar