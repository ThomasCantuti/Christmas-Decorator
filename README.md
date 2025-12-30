# Christmas Decorator AI 🎄

This application uses AI to decorate your room photos with Christmas themes.

## Architecture

- **Frontend**: React (Vite) with a premium dark theme.
- **Backend**: FastAPI (Python).
- **AI Framework**: Datapizza.ai (orchestration).
- **Runtime**: `llama.cpp` (for VLM/LLM inference) & Stable Diffusion (via diffusers) for image generation.

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
   To run locally with `llama.cpp`, you need to download the LLaVA models (or compatible) and place them in `backend/models/`:
   - `llava-v1.5-7b-Q4_K.gguf` (Main VLM)
   - `mmproj-model-f16.gguf` (CLIP projector)
   
   *If models are not found, the backend will run in MOCK mode (simulating the decoration).*

### 2. Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the App

You can run both servers manually or use the helper script.

**Manual:**
- Terminal 1 (Backend): `python backend/main.py`
- Terminal 2 (Frontend): `npm run dev` in `frontend/` directory.

The frontend will act as the interface, uploading images to the backend which processes them using the AI agent.

## Usage

1. Open the web app (usually `http://localhost:5173`).
2. Upload a photo of a room or office.
3. (Optional) Add a specific text request (e.g., "Make it icy blue theme").
4. Click Decorate!

## Validation Logic

- The AI first checks if the image is a valid indoor environment using the VLM.
- If text is provided, it checks if the request is relevant to the image.
- If valid, it generates a decoration prompt and edits the image.
