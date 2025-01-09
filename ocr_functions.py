from ocrmypdf import ocr, hookimpl
from ocrmypdf.pluginspec import ProgressBar
from pathlib import Path

_ocr_progress = {}

def do_ocr_in_background(input_pdf_path: Path, output_pdf_path: Path) -> None:
    """
    Perform OCR in the background using `ocrmypdf`. This function:
      1. Clears the previous progress state.
      2. Runs `ocrmypdf.ocr` with a custom plugin (`MyProgressBar`) that tracks progress.
      3. On completion or exception, clears the progress again.
      4. Sets the 'terminated' state to True indicating the task has finished (successfully or otherwise).

    Args:
        input_pdf_path (Path): The path to the original input PDF file.
        output_pdf_path (Path): The path to the output OCR-processed PDF.
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
        raise Exception("Error running ocrmypdf in background.") from exc
    finally:
        clear_ocr_progress()
        set_ocr_progress("terminated", True)

def set_ocr_progress(key: str, value) -> None:
    """
    Update or create a key-value pair in the global OCR progress dictionary.

    Args:
        key (str): The key to update or create.
        value (any): The value to store under `key`.
    """
    _ocr_progress[key] = value

def get_ocr_progress() -> dict:
    """
    Retrieve the global dictionary containing OCR progress information.

    Returns:
        dict: The current dictionary holding all progress-related data.
    """
    return _ocr_progress

def clear_ocr_progress() -> None:
    """
    Clear all key-value pairs from the global OCR progress dictionary.
    """
    _ocr_progress.clear()

class MyProgressBar(ProgressBar):
    """
    A custom progress bar class to track OCR progress in real-time. 
    Integrates with ocrmypdf's plugin system by implementing the 
    `get_progressbar_class()` hook.
    """

    def __init__(
        self,
        total: int | None,
        desc: str | None,
        unit: str | None,
        disable: bool = False,
    ):
        """
        Initialize the custom progress bar, clearing any existing progress and 
        setting initial values in the global progress dictionary.

        Args:
            total (int | None): The total amount of work to be done (e.g., total pages).
            desc (str | None): Description or label of the progress bar.
            unit (str | None): The unit of measurement (e.g., 'page', '%', etc.).
            disable (bool): Whether to disable the progress bar output.
        """
        self.progress_bar = 0
        clear_ocr_progress()
        set_ocr_progress("total", total)
        set_ocr_progress("desc", desc)
        set_ocr_progress("unit", unit)
        set_ocr_progress("progress_bar", self.progress_bar)
        print(get_ocr_progress())  # For debug/logging purposes

    def update(self, n=1, completed=None) -> None:
        """
        Update the progress bar. If `completed` is provided, the progress is set 
        directly to `completed`. Otherwise, it increments by `n`.

        Args:
            n (int): The amount to increment the progress bar by if `completed` is None.
            completed (int | None): If provided, the progress bar is set to this value instead.
        """
        if completed is not None:
            self.progress_bar = completed
        else:
            self.progress_bar += n

        set_ocr_progress("progress_bar", self.progress_bar)
        print(get_ocr_progress())  # For debug/logging purposes

    def __enter__(self):
        """
        Enter the runtime context related to this object. 
        Returns the progress bar instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Exit the runtime context, returning False so any exception is propagated.
        
        Args:
            exc_type: The exception type (if any).
            exc_value: The exception value (if any).
            traceback: The traceback (if any).
        
        Returns:
            bool: Always returns False to let exceptions propagate.
        """
        return False

@hookimpl
def get_progressbar_class():
    """
    Hook implementation to tell `ocrmypdf` which ProgressBar class to use.
    
    Returns:
        MyProgressBar: The custom progress bar class that will be used by `ocrmypdf`.
    """
    return MyProgressBar