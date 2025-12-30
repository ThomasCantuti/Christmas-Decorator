# Configuration
MODELS_DIR="models"
TEXT_MODEL="gemma-3-270m-it-Q4_K_M.gguf"
VLM_MODEL="gemma-3-4b-it-Q4_K_M.gguf"
VLM_MMPROJ="mmproj-F16.gguf"
DIFFUSION_MODEL="Qwen-Image-Edit-2511-Q4_K_M.gguf"

# Check if llama-server is installed
if ! command -v llama-server &> /dev/null; then
    echo "❌ Error: llama-server is not found in PATH."
    echo "Please install llama.cpp and ensure llama-server is available."
    exit 1
fi

echo "🎄 Starting Christmas Decorator Model Servers..."

# Function to kill child processes on exit
cleanup() {
    echo "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

# Start Text Model Server (Port 8081)
if [ -f "$MODELS_DIR/$TEXT_MODEL" ]; then
    echo "🚀 Starting Text Model ($TEXT_MODEL) on port 8081..."
    llama-server -m "$MODELS_DIR/$TEXT_MODEL" --port 8081 --host 127.0.0.1 > llama_text.log 2>&1 &
    TEXT_PID=$!
else
    echo "⚠️  Text model not found at $MODELS_DIR/$TEXT_MODEL"
fi

# Start VLM Model Server (Port 8082)
if [ -f "$MODELS_DIR/$VLM_MODEL" ]; then
    echo "🚀 Starting VLM Model ($VLM_MODEL) on port 8082..."
    
    CMD_ARGS="-m $MODELS_DIR/$VLM_MODEL --port 8082 --host 127.0.0.1"
    
    # Add mmproj if it exists
    if [ -f "$MODELS_DIR/$VLM_MMPROJ" ]; then
        echo "   + with mmproj: $VLM_MMPROJ"
        CMD_ARGS="$CMD_ARGS --mmproj $MODELS_DIR/$VLM_MMPROJ"
    else
        echo "   ⚠️  mmproj NOT FOUND ($VLM_MMPROJ) - VLM might fail on images!"
    fi
    
    llama-server $CMD_ARGS > llama_vlm.log 2>&1 &
    VLM_PID=$!
else
    echo "⚠️  VLM model not found at $MODELS_DIR/$VLM_MODEL"
fi

# Start Diffusion/Edit Model Server (Port 8083)
if [ -f "$MODELS_DIR/$DIFFUSION_MODEL" ]; then
    echo "🚀 Starting Diffusion Model ($DIFFUSION_MODEL) on port 8083..."
    llama-server -m "$MODELS_DIR/$DIFFUSION_MODEL" --port 8083 --host 127.0.0.1 > llama_diff.log 2>&1 &
    DIFF_PID=$!
else
    echo "⚠️  Diffusion model not found at $MODELS_DIR/$DIFFUSION_MODEL"
fi

echo "✅ Servers are starting in the background."
echo "   - Text: localhost:8081 (Log: llama_text.log)"
echo "   - VLM:  localhost:8082 (Log: llama_vlm.log)"
echo "   - Diff: localhost:8083 (Log: llama_diff.log)"
echo ""
echo "Press Ctrl+C to stop all servers."

# Wait indefinitely
wait
