# Christmas Decorator AI 🎄

This application uses specific AI agents to decorate your room photos with Christmas themes. It uses a multi-agent system powered by local LLMs, VLMs, and cloud-based image generation.

## Showcase

https://github.com/user-attachments/assets/91e779ec-0727-4470-9ef2-77ecf25ac23c

## Project Evolution

> **Note on Model Selection**: The original scope of this project was to use **only open-weight models** running locally. However, the **Qwen Image Edit** model proved to be too resource-intensive for local execution—even on laptops equipped with an **NVIDIA GeForce RTX 5090** and **CUDA enabled**. Due to these hardware constraints, the image generation component was migrated to the **Gemini Flash Image model**, which requires a Google API key.

## Architecture

- **Frontend**: React (Vite) with a premium dark theme.
- **Backend**: FastAPI (Python) serving as the agent orchestrator.
- **AI Framework**: [Datapizza.ai](https://github.com/datapizza/datapizza) agents for validation, planning, and execution.
- **Model Runtime**: `llama.cpp` server for local vision model.
- **Models**:
  - **Vision Agent**: `Gemma 3 4B` (Image Understanding) — *local*
  - **Decorator Agent**: `Gemini Flash Image` (Image Generation) — *cloud API*

## Prerequisites

1. **Python 3.10+** and **Node.js**.
2. **llama.cpp**: You must have `llama-server` installed and available in your system PATH.
   - Mac/Linux: Build from source (`make`) or install via brew if available.
   - Windows: Download pre-built binaries.
3. **Google Gemini API Key**: Required for the image generation feature.
   - Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

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
   Run the helper script to download the required GGUF models (Gemma 3):
   ```bash
   python download_models.py
   ```
4. **Configure API Key**:
   Create a `.env` file in the `backend` directory and add your Gemini API key (follow the `.env.example` file):
   ```bash
   GEMINI_API_KEY=your_api_key_here
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
Start the `llama-server` instances for Vision model.
```bash
cd backend
chmod +x start_model.sh
./start_model.sh
```
*Wait until you see "Server started with PID `PID`" and the logs indicate they are listening on port 8081.*

**Terminal 2: Backend API**
Start the FastAPI orchestrator.
```bash
cd backend
python3 main.py
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
