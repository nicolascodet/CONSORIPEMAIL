#!/bin/bash

# Function to check if a port is in use
is_port_in_use() {
    lsof -i:"$1" >/dev/null 2>&1
    return $?
}

# Function to kill process using a port
kill_port() {
    lsof -ti:"$1" | xargs kill -9 2>/dev/null
}

# Kill any existing processes
echo "Cleaning up existing processes..."
if is_port_in_use 8000; then
    kill_port 8000
fi
if is_port_in_use 3000; then
    kill_port 3000
fi

# Create necessary directories
mkdir -p backend/attachments

# Start backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m uvicorn main:app --reload --port 8000 &
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 2

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm install >/dev/null 2>&1
npm run dev &
cd ..

echo "Servers are running. Press Ctrl+C to stop."

# Wait for both processes
wait
