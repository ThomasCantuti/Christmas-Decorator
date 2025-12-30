# Christmas Decorator AI 🎄

This application uses specific AI agents to decorate your room photos with Christmas themes. It uses a multi-agent system powered by local LLMs and VLMs.

## Architecture

- **Frontend**: React (Vite) with a premium dark theme.
- **Backend**: FastAPI (Python) serving as the agent orchestrator.
- **AI Engine**: [Datapizza.ai](https://github.com/datapizza/datapizza) agents for validation, planning, and execution.
- **Model Runtime**: `llama.cpp` server (running 3 dedicated micro-services).
- **Models**:
  - **Text Agent**: `Gemma 3 270M` (Reasoning & Validation)
  - **Vision Agent**: `Gemma 3 4B` (Image Understanding)
  - **Decorator Agent**: `Qwen Image Edit` (Image-to-Image Generation)

## Prerequisites

1. **Python 3.10+** and **Node.js**.
2. **llama.cpp**: You must have `llama-server` installed and available in your system PATH.
   - Mac/Linux: Build from source (`make`) or install via brew if available.
   - Windows: Download pre-built binaries.

## Setup

### 1. Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Download Models**:
   Run the helper script to download the required GGUF models (Gemma 3 & Qwen):
   ```bash
   python download_models.py
   ```

### 2. Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the App

The application requires 3 terminals to run the models, backend, and frontend concurrently.

**Terminal 1: Model Servers**
Start the `llama-server` instances for Text, Vision, and Diffusion models.
```bash
cd backend
chmod +x start_models.sh
./start_models.sh
```
*Wait until you see "Servers are starting" and the logs indicate they are listening on ports 8081, 8082, and 8083.*

**Terminal 2: Backend API**
Start the FastAPI orchestrator.
```bash
cd backend
# source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 3: Frontend**
Start the web interface.
```bash
cd frontend
npm run dev
```

## Usage

1. Open the web app (usually `http://localhost:5173`).
2. Upload a photo of a room or office.
3. (Optional) Add a specific text request (e.g., "Make it icy blue theme").
4. **Decorate!** The agents will:
   - **Validate** the image is a room.
   - **Plan** the decoration strategy.
   - **Generate** the new festive image.

## Troubleshooting

- **"llama-server not found"**: Ensure built `llama.cpp` binaries are in your PATH.
- **Model Download Errors**: delete the `backend/models` folder and retry `python download_models.py`.
- **Validation Fails**: The VLM (Gemma 3 4B) might be strict; ensure the room is clearly visible.
