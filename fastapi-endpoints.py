import argparse
import logging
import shutil
import uuid
from pathlib import Path

import ocrmypdf
from PIL import Image
from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.ocr_functions import do_ocr_in_background, get_ocr_progress

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--host",
    type=str,
    default="localhost",
    help="The host address to bind the server to.",
)
parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="The port number to bind the server to.",
)

args = parser.parse_args()


ocr_router = FastAPI()
ocr_router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# Load demo HTML for the root endpoint
with open("src/demo.html", "r") as f:
    html = f.read()
html = html.replace("API_URL", f"http://{args.host}:{args.port}")


@ocr_router.get("/")
async def get():
    return HTMLResponse(html)

@ocr_router.post("/ocr-pdf")
async def ocr_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Receives a PDF or an image file. If it's an image, convert it to PDF first,
    then run OCR. Returns an ID that can be used to track progress and
    retrieve the final OCR-processed PDF.
    """
    # Generate a unique name (UUID) for this file's processing
    file_id = str(uuid.uuid4())

    input_pdf_path = UPLOAD_FOLDER / f"{file_id}.pdf"
    output_pdf_path = UPLOAD_FOLDER / f"{file_id}_ocr.pdf"

    try:
        if file.content_type == "application/pdf":
            with open(input_pdf_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            temp_image_path = UPLOAD_FOLDER / f"{file_id}_temp"
            with open(temp_image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            pil_image = Image.open(temp_image_path).convert("RGB")
            pil_image.save(input_pdf_path, "PDF", resolution=100.0)

            temp_image_path.unlink(missing_ok=True)

        # Trigger background OCR task
        background_tasks.add_task(do_ocr_in_background, input_pdf_path, output_pdf_path)

    except Exception as e:
        logger.exception("Error during OCR processing.")
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return {"id": file_id}


@ocr_router.get("/ocr-pdf/progress/")
def get_progress():
    """
    Returns the current OCR progress (0-100).
    - If progress is -1, it indicates an error.
    """
    return get_ocr_progress()


@ocr_router.get("/ocr-pdf/results/{file_id}")
async def get_ocr_results(file_id: str):
    """
    Check if the OCR-processed PDF is ready. 
    Returns:
      - finished: Boolean indicating if the OCR process is complete
      - download_url: Path to download the OCR PDF if ready
    """
    file_path = UPLOAD_FOLDER / f"{file_id}_ocr.pdf"
    if not file_path.exists():
        return {
            "extracted_text": "",
            "finished": False,
            "download_url": "",
        }
    return {
        "finished": True,
        "download_url": f"/ocr-pdf/download/{file_id}_ocr.pdf",
    }


@ocr_router.get("/ocr-pdf/download/{filename}")
async def download_ocr_pdf(filename: str):
    """
    Download the OCR-processed PDF by filename.
    """
    file_path = UPLOAD_FOLDER / filename
    if not file_path.exists():
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="result.pdf",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fastapi-endpoints:ocr_router", host="localhost", port=8000, reload=True)