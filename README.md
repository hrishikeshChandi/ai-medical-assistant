# AI Medical Assistant

> Student project — a modern FastAPI service that analyzes chest X-ray images combined with patient context using LLMs to generate medical summaries enriched with real-world hospital and medicine data.

> **⚠️ Not a substitute for professional medical advice. Educational use only.**

---

## Overview

AI Medical Assistant is a FastAPI application that accepts chest X-ray images along with patient context (symptoms, current medications, diet, exercise). These inputs are processed through a multi-modal AI pipeline to generate structured medical summaries enriched with side-effect analysis and resource information.

> Note:

- Audio analysis module is currently under development.
- Chest X-ray model training is not pushed to GitHub because of size constraints. Run `main.ipynb` in `ai/image/` folder first.

---

## Tech Stack

[![Python](https://img.shields.io/badge/Python-3.12.4-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-green.svg)](https://fastapi.tiangolo.com/)
[![UV](https://img.shields.io/badge/UV-Package_Manager-purple.svg)](https://github.com/astral-sh/uv)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep_Learning-orange.svg)](https://pytorch.org/)
[![Redis](https://img.shields.io/badge/Redis-Queue-red.svg)](https://redis.io/)

- FastAPI – REST API
- LangChain + Groq – LLM orchestration
- EfficientNet-B2 (fine-tuned on a balanced chest X-ray dataset) – Image analysis
- Redis + RQ – Background job processing
- Selenium – Medicine price/link scraping
- UV – Dependency & environment management

## Key Features

- Upload chest X-ray images for AI-powered analysis and summary generation
- Combine patient symptoms, medications, and lifestyle data with structured medical summarization and reasoning.
- Extract medicine side effects using structured LLM prompts with Pydantic validation
- Scrape live web-scraped hospital availability and medicine price comparisons via Selenium
- Generate downloadable medical reports, with async Redis job queues used for hospital data scraping

---

## Project Structure

```bash
ai-medical-assistant/
├── ai/
│ ├── audio/ # Audio processing components (in development)
│ ├── image/ # Computer vision components
│ ├── base_models.py # Pydantic schemas for structured outputs
│ ├── llms.py # LLM pipeline setup (LangChain + Groq)
│ ├── model_prompts.py # LLM prompt templates
│ └── service.py # Core AI service functions
├── client/
│ └── rq_client.py # Redis queue client setup
├── config/
│ ├── .env # Environment variables (template)
│ └── constants.py # Configuration constants
├── data/
│ ├── cities.json # Supported cities for hospital search
│ └── final_instructions.txt # Report template
├── routers/
│ ├── scraper.py # Hospital data endpoints
│ ├── uploads.py # File upload endpoints
│ └── jobs.py # Job status endpoints
├── uploads/ # Temporary file storage
├── utilities/
│ ├── driver.py # Selenium webdriver management
│ ├── jobs.py # Job processing functions
│ ├── scraper_utilities.py # Web scraping logic
│ └── upload_utilities.py # File processing & cleanup
├── docker-compose.yaml # Containerized deployment setup
├── main.py # FastAPI app entry point
├── pyproject.toml # UV project configuration
└── uv.lock # UV lock file for reproducible builds
```

---

## Setup Instructions (Using UV Package Manager)

### Prerequisites

- Python 3.10+
- UV Package Manager
- Redis
- Groq API key
- Firefox browser
- Docker

### Quick Start

- Clone the repo

  ```bash
  git clone https://github.com/hrishikeshChandi/ai-medical-assistant.git
  cd ai-medical-assistant
  ```

- Setup the environment

  ```bash
  uv sync
  source .venv/bin/activate # Linux/macOS

  # .venv\Scripts\activate # Windows
  ```

- Start the redis server

  ```bash # Start redis server
  docker-compose up -d
  ```

- Open another terminal(s) to start the rq workers

  ```bash
  uv run rq worker --url redis://localhost:6379
  ```

- Start the FastAPI server

  ```bash
  uv run main.py
  ```

- Create `config/.env`:

  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```

## Usage

### API Endpoints

`GET /`

- Health check endpoint
- Returns: `{"message": "yeye api is working :)"}`

`GET /scraper/hospitals_data?city={city_name}`

- Fetches live hospital availability data for the specified city
- Query parameter: `city` (required, e.g., `city=Mumbai`)
- Returns: `{"status": "queued", "job_id": "job-id-here"}`
- Background job scrapes hospital data from Practo
- Check job status via `/jobs/job_status/{job_id}`

`GET /jobs/job_status/{job_id}`

- Check status of background jobs
- Path parameter: `job_id` (from hospital scraping or upload endpoints)
- Returns: `{"status": "queued|in progress|completed|failed", "data": {...}}`
- For completed hospital scraping: returns list of hospitals with names, locations, ratings, fees
- For completed upload processing: returns medical summary with side effects and medicine price links

`POST /uploads/image_upload`

- Upload chest X-ray images for analysis
- **Parameters** (query): `diet`, `symptoms`, `current_medicines`, `exercise`, `user_id`, `additional_info` (optional)
- **Files**: Multiple image files allowed (jpg, jpeg, png, gif, bmp, webp, tiff)
- **Returns**: `{"status": "queued", "job_id": "job-id-here"}`

`POST /uploads/audio_upload`

- Upload audio files for analysis (stub implementation)
- Same parameters as image upload
- **Files**: Multiple audio files allowed (mp3, wav, aac, flac, ogg, m4a, wma)
- **Note**: Audio analysis module is under development

`GET /uploads/download/{user_id}`

- Download generated medical report
- Path parameter: `user_id` (same as used in upload)
- Returns: `reports.txt` file with medical summary
- File saved at: `uploads/{user_id}/reports.txt`

---

## Key Components

### Architecture

1. **Image Analysis Pipeline**
   - Chest X-ray classification using EfficientNet-B2
   - Fine-tuned on balanced chest X-ray dataset (Kaggle)
   - Binary classification: Normal vs. Pneumonia
   - Model inference with PyTorch

2. **LLM Orchestration Layer**
   - **BioGPT Chain**: Generates medical summaries from symptoms, medications, and image results
   - **Side Effects Chain**: Extracts 2-3 common side effects for each medicine
   - **Final Chain**: Combines all inputs into structured medical report
   - Powered by Llama 3.3 70B via Groq API with temperature control

3. **Web Scraping Engine**
   - Hospital data scraping from Practo (names, locations, ratings, consultation fees)
   - Medicine price comparison across PharmEasy and MedPlus
   - Selenium with Firefox headless browser
   - City-based filtering with validation

4. **Job Processing System**
   - Redis/Valkey queue for background task management
   - RQ (Redis Queue) for job scheduling and execution
   - Job status tracking with `/jobs/job_status/{job_id}` endpoint
   - Async processing for long-running operations

5. **File Lifecycle Management**
   - Multi-file upload support with validation
   - Temporary storage in user-specific folders
   - Report generation in `uploads/{user_id}/reports.txt`
   - Automatic cleanup post-processing

### System Features

- **Modular API Design**: Three dedicated routers (`scraper`, `uploads`, `jobs`) with clear separation
- **Structured Validation**: Pydantic models enforce consistent LLM outputs and API responses
- **Real-time Processing**: Live web scraping integrated with AI analysis
- **Scalable Job Queue**: Background processing for resource-intensive operations
- **Comprehensive Error Handling**: Graceful degradation for external service failures
- **Developer Experience**: Full API documentation at `/docs`, consistent response formats
- **Resource Efficiency**: Automatic cleanup of temporary files and browser instances

---

## Troubleshooting

### Common Issues

**Missing GROQ_API_KEY:**

- Symptom: Errors when `ai/llms.py` initializes the LLM
- Fix: Set `GROQ_API_KEY` in `.env` file in `config/` directory

**Redis Connection Failed:**

```bash
# Check if Redis is running
redis-cli ping
```

**Selenium Driver Issues:**

- Ensure Firefox/Chrome is installed
- Update `utilities/driver.py` for your browser version

**File Upload Errors (415 Unsupported Media Type):**

- Use allowed file extensions listed in the Usage section

**Permission Errors Writing to `uploads/`:**

- Ensure process has write permissions in repository folder
- `uploads/` is created automatically, but check permissions

**Port Already in Use:**

- Change the `PORT` in `config/constants.py`

---

## License

MIT License — You may use and modify this project under the terms of the MIT license.

---
