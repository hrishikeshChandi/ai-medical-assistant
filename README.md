# AI Medical Assistant

> Student project — an experimental FastAPI service that combines uploaded medical images/audio and user context with LLMs to generate a concise medical summary and medicine-related information.

> **Not a substitute for professional medical advice.**

---

## Overview

AI Medical Assistant is a prototype FastAPI application that accepts user-provided context (symptoms, diet, medications, exercise) along with uploaded medical images or audio. These inputs are processed using AI models and LLMs to generate a structured medical summary, medicine side-effects, and reference links.

This project is built for **learning and experimentation**, not for clinical use.

---

## Tech Stack

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![UV](https://img.shields.io/badge/UV-Package_Manager-purple.svg)](https://github.com/astral-sh/uv)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep_Learning-orange.svg)](https://pytorch.org/)

- FastAPI – REST API
- LangChain + Groq – LLM orchestration
- EfficientNet (experimental) – Image analysis
- Redis + RQ – Background job processing
- Selenium – Medicine price/link scraping
- UV – Dependency & environment management

## Key Features

- Upload medical images and receive an AI-generated summary
- Upload medical audio (partial / WIP support)
- Combine user context (symptoms, medicines, lifestyle) with AI analysis
- Extract medicine side effects using LLM prompts
- Scrape medicine prices & reference links
- Generate a downloadable medical report

---

## Project Structure

```bash
ai-medical-assistant/
├── ai/
│ ├── audio/ # Audio processing components
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
│ └── uploads.py # File upload endpoints
├── utilities/
│ ├── driver.py # Selenium webdriver management
│ ├── scraper_job.py # Async scraping jobs
│ ├── scraper_utilities.py # Web scraping logic
│ └── upload_utilities.py # File processing & cleanup
├── uploads/ # Temporary file storage
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

### Quick Start

```bash
# Clone the repo
git clone https://github.com/hrishikeshChandi/ai-medical-assistant.git
cd ai-medical-assistant

uv sync
source .venv/bin/activate # Linux/macOS

# .venv\Scripts\activate # Windows

uv run main.py
```

Create `config/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

### API Endpoints

`POST /image_upload`

- Upload medical images (jpg, jpeg, png)
- Includes user context (symptoms, medicines, etc.)

`POST /audio_upload`

- Upload audio files (mp3, wav, aac)
- Work in progress

`GET /download`

- Download the generated medical report

### Example Request (Image Upload)

```bash
curl -X POST "http://127.0.0.1:1200/image_upload" \
  -F "diet=vegetarian" \
  -F "symptoms=cough, breathlessness" \
  -F "current_medicines=paracetamol" \
  -F "files=@chest_xray.jpg"
```

### Example Request (Download Report)

```bash
curl -O "http://127.0.0.1:1200/download"
```

### Response Format

```json
{
  "response": "<LLM-generated summary and scraped info>",
  "time_taken": "X seconds"
}
```

---

## Key Components

### AI Pipeline Architecture

1. **Image Analysis**: Chest X-ray classification using EfficientNet-B2
2. **LLM Summarization**: Clinical reasoning via Llama 3.3 70B with Pydantic schema validation
3. **Side Effects Analysis**: Medicine-specific risk assessment via structured LLM prompts
4. **Resource Enrichment**: Real-time medicine price scraping via Selenium
5. **Async Processing**: Redis + RQ for scalable background job handling

### System Features

- **Modular Design**: Separate routers, utilities, and AI components
- **Async Processing**: Redis+RQ for background job handling
- **Structured Outputs**: Pydantic validation for LLM responses
- **Error Resilience**: Comprehensive exception handling
- **File Management**: Automatic cleanup of temporary files

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

## Disclaimer

**⚠️ Educational use only.**
This project and its outputs are not medical advice and must not be used for diagnosis or treatment. Always consult a qualified medical professional.

This is a student project and experimental prototype.

---

## License

MIT License — You may use and modify this project under the terms of the MIT license.

---

