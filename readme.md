# OCR with Progress Demo

This repository demonstrates how to integrate [ocrmypdf](https://github.com/ocrmypdf/OCRmyPDF) with a custom plugin to track and report progress information. The goal is to show how you can use a **custom FastAPI plugin** to intercept OCR progress updates and **pass** that progress to **an external client**—in this case, a simple webpage that polls a REST API endpoint for status updates.

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Key Files](#key-files)
- [Installation](#installation)
- [Running the Demo](#running-the-demo)
- [How It Works](#how-it-works)
- [Additional Notes](#additional-notes)

---

## Overview

- **Purpose**: The main purpose is to demonstrate how to capture and communicate progress from a long-running task (OCR via `ocrmypdf`) to a web client, using a custom FastAPI endpoint and a polling mechanism.
- **Highlights**:
  - Implements a **custom FastAPI plugin** that hooks into the `ocrmypdf` progress bar system.
  - Stores real-time progress updates in a global dictionary.
  - Exposes a dedicated endpoint to **poll** OCR progress from the frontend.
  - Frontend displays a **progress bar** and downloads the resulting PDF once OCR processing completes.

---

## Project Structure

.
├── demo.html
├── fastapi-endpoints.py
├── ocr_functions.py
├── requirements.txt
└── readme.md  (this file)

1. **demo.html**  
   A simple HTML file showcasing an OCR upload form, progress bar, and result display.  
2. **fastapi-endpoints.py**  
   Contains the FastAPI setup, endpoints for uploading files, checking progress, retrieving results, and downloading the final PDF.  
3. **ocr_functions.py**  
   Contains the custom `ocrmypdf` plugin and logic (`MyProgressBar`) that captures and updates a global progress dictionary.
4. **requirements.txt**  
   Lists Python dependencies.
5. **readme.md**  
   The documentation you’re currently reading.

---

## Key Files

### demo.html

- Presents a form for uploading a PDF or image file.
- Initiates the OCR process by calling the `/ocr-pdf` endpoint (via `fetch`).
- Continuously polls the `/ocr-pdf/progress/` endpoint to update the progress bar.
- Once the OCR process finishes, fetches the final PDF download URL and displays a “Download PDF” link.

### fastapi-endpoints.py

- Creates a FastAPI app.
- Implements `/ocr-pdf` to handle file uploads (PDF or image) and trigger background OCR tasks.
- Implements `/ocr-pdf/progress/` to return the current progress state as JSON.
- Implements `/ocr-pdf/results/{file_id}` to check OCR completion and retrieve the final PDF’s download link.
- Demonstrates usage of **BackgroundTasks** to handle long-running tasks without blocking the main thread.

### ocr_functions.py

- Implements a **custom plugin** for `ocrmypdf` that updates `_ocr_progress` in real time.
- Uses `@hookimpl` to attach `MyProgressBar` to the internal progress bar mechanics of `ocrmypdf`.
- Stores progress details (like total pages, current page, etc.) in a global dictionary, making it easy for the FastAPI server to provide real-time status to the frontend.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourname/ocr-progress-demo.git
   cd ocr-progress-demo
   ```

	2.	Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

	3.	Install system dependencies for OCRmyPDF if you haven’t already.

Refer to OCRmyPDF documentation for detailed installation instructions (e.g., Tesseract, Ghostscript, and additional system libraries).

##Running the Demo
	1.	Start the FastAPI server:

    ```python fastapi-endpoints.py```


	2.	Open your browser at:

    ```http://localhost:8000```


	3.	Upload a PDF or image from the main page and press the “Start OCR” button.
	4.	Watch the progress bar update as OCRmyPDF processes your file.
	5.	Once completed, click the “Download PDF” link to get the OCR-processed PDF.

How It Works
	1.	Upload
A file (PDF or image) is uploaded to the /ocr-pdf endpoint. If the file is an image, it’s converted into PDF format on-the-fly using PIL.
	2.	Background OCR
The OCR process runs in a background task via BackgroundTasks from FastAPI.
	•	ocrmypdf.ocr() is called with a custom plugin (MyProgressBar) that tracks progress events.
	3.	Progress Updates
	•	The MyProgressBar class in ocr_functions.py receives regular updates during OCR.
	•	These updates are stored in a global dictionary (_ocr_progress).
	•	The /ocr-pdf/progress/ endpoint returns the current progress dictionary as JSON.
	4.	Polling
	•	The frontend’s JavaScript periodically calls the /ocr-pdf/progress/ endpoint (every 1 second, for example).
	•	The progress bar is updated accordingly.
	5.	Completion & Results
	•	When OCR completes, the final PDF becomes available, and the _ocr_progress dictionary indicates the process has terminated.
	•	The frontend then calls /ocr-pdf/results/{file_id} to retrieve the download URL and displays a link to the new OCR-processed PDF.

Additional Notes
	•	Purpose of the custom plugin:
This repository emphasizes the integration of a custom FastAPI plugin with ocrmypdf to expose progress updates to a web client. It’s not meant to be a full-fledged production-ready OCR service but rather a learning/demo project.
	•	Extensibility:
You can easily adapt this approach to:
	•	Monitor progress for other tasks (e.g., video processing, data analysis).
	•	Use WebSockets instead of HTTP polling to push progress updates in real-time.
	•	Persist progress and result files in a database or cloud storage.
	•	Dependencies:
	•	Python >= 3.8 (tested on 3.9+).
	•	ocrmypdf, Pillow (PIL), fastapi, uvicorn, etc.
	•	Tesseract and other system requirements for ocrmypdf.

Feel free to explore, fork, and adapt to fit your needs!

