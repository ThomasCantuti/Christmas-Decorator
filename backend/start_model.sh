# Configuration
MODELS_DIR="models"
MODEL_NAME="gemma-3-4b-it-Q4_K_M.gguf"
MMPROJ_NAME="mmproj-F16.gguf"

# Check for llama-server
if [ -f "./llama-server" ]; then
    SERVER_CMD="./llama-server"
    echo "✅ Using local llama-server: $SERVER_CMD"
elif command -v llama-server &> /dev/null; then
    SERVER_CMD="llama-server"
    echo "✅ Using system llama-server: $(which llama-server)"
else
    echo "❌ Error: llama-server is not found in PATH or current directory."
    echo "Please install llama.cpp and ensure llama-server is available."
    exit 1
fi

echo "🎄 Starting Christmas Decorator Model Server (Gemma 3)..."

# Function to kill child processes on exit
cleanup() {
    echo "Shutting down server..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

# Start Model Server (Port 8081)
if [ -f "$MODELS_DIR/$MODEL_NAME" ]; then
    echo "🚀 Starting Gemma 3 Model ($MODEL_NAME) on port 8081..."
    
    CMD_ARGS="-m $MODELS_DIR/$MODEL_NAME --port 8081 --host 127.0.0.1"
    
    # Add mmproj if it exists
    if [ -f "$MODELS_DIR/$MMPROJ_NAME" ]; then
        echo "   + with mmproj: $MMPROJ_NAME"
        CMD_ARGS="$CMD_ARGS --mmproj $MODELS_DIR/$MMPROJ_NAME"
    else
        echo "   ⚠️  mmproj NOT FOUND ($MMPROJ_NAME) - Vision capabilities might fail!"
    fi
    
    $SERVER_CMD $CMD_ARGS > llama_server.log 2>&1 &
    PID=$!
    
    echo "✅ Server started with PID $PID"
    echo "   - Address: http://localhost:8081"
    echo "   - Log: llama_server.log"
else
    echo "❌ Error: Model not found at $MODELS_DIR/$MODEL_NAME"
    exit 1
fi

echo ""
echo "Press Ctrl+C to stop the server."

# Wait indefinitely
wait
