#!/bin/bash

# Cognitrix Process Manager
# Usage: ./start.sh [start|stop|status|restart|force-stop|logs|help] [port]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/process.pid"

# Create log directory if it doesn't exist
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Generate log file with current datetime
CURRENT_DATETIME=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/cognitrix_$CURRENT_DATETIME.log"

DEFAULT_PORT=3001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to get PID by port
get_pid_by_port() {
    local port=$1
    lsof -ti :$port 2>/dev/null
}

# Function to start the application
start_app() {
    local port=${1:-$DEFAULT_PORT}

    print_info "🧠 Starting Cognitrix on port $port..."

    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local existing_pid=$(cat "$PID_FILE")
        if ps -p $existing_pid > /dev/null 2>&1; then
            print_warning "Cognitrix is already running with PID $existing_pid"
            local running_port=$(lsof -p $existing_pid -i -a | grep LISTEN | awk '{print $9}' | cut -d: -f2)
            if [ -n "$running_port" ]; then
                print_info "Running on port: $running_port"
                print_info "Access at: http://localhost:$running_port"
            fi
            return 1
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi

    # Check if port is already in use
    if check_port $port; then
        local existing_pid=$(get_pid_by_port $port)
        print_error "Port $port is already in use by PID $existing_pid"
        print_info "Use 'lsof -i :$port' to see what's using it"
        print_info "Or try a different port: $0 start <port_number>"
        return 1
    fi

    # Check if app directory exists
    if [ ! -d "$SCRIPT_DIR/app" ]; then
        print_error "app directory not found in $SCRIPT_DIR"
        print_info "Make sure you're running this script from the Cognitrix root directory"
        return 1
    fi

    # Check if app.py exists
    if [ ! -f "$SCRIPT_DIR/app/app.py" ]; then
        print_error "app.py not found in $SCRIPT_DIR/app/"
        return 1
    fi

    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment not activated!"
        print_info "Please activate your virtual environment first:"
        print_info "  source venv/bin/activate"
        print_info "  $0 start"
        return 1
    fi

    print_info "Using virtual environment: $VIRTUAL_ENV"

    # Check if Flask is installed
    if ! python -c "import flask" 2>/dev/null; then
        print_error "Flask not found in current environment"
        print_info "Install requirements: pip install -r requirements.txt"
        return 1
    fi

    # Detect Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Neither python nor python3 command found"
        return 1
    fi

    # Start the application in background
    print_status "Starting Cognitrix..."
    nohup bash -c "
        cd '$SCRIPT_DIR/app'
        PORT=$port $PYTHON_CMD app.py
    " > "$LOG_FILE" 2>&1 &

    local app_pid=$!
    echo $app_pid > "$PID_FILE"

    # Wait a moment and check if it started successfully
    sleep 3
    if ps -p $app_pid > /dev/null 2>&1; then
        print_status "🎉 Cognitrix started successfully!"
        print_info "PID: $app_pid"
        print_info "Port: $port"
        print_info "Log file: $LOG_FILE"
        print_info "Access at: http://localhost:$port"
        print_info ""
        print_info "📝 To stop: $0 stop"
        print_info "📊 To check status: $0 status"
        print_info "📋 To view logs: $0 logs"
        print_info "🔄 To restart: $0 restart"
    else
        print_error "Failed to start Cognitrix"
        print_info "Check log file: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the application
stop_app() {
    print_info "🛑 Stopping Cognitrix..."

    local stopped_any=false

    # Method 1: Try to stop using PID file
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        print_info "Found PID file with PID: $pid"

        if ps -p $pid > /dev/null 2>&1; then
            print_info "Stopping process $pid..."

            # Get the port this process is using
            local port=$(lsof -p $pid -i -a 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2)
            if [ -n "$port" ]; then
                print_info "Process was running on port: $port"
            fi

            # Try graceful shutdown first
            kill $pid 2>/dev/null

            # Wait for graceful shutdown
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
                printf "."
            done
            echo

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                print_warning "Process didn't stop gracefully, force killing..."
                kill -9 $pid 2>/dev/null
                sleep 1
            fi

            if ps -p $pid > /dev/null 2>&1; then
                print_error "Failed to stop process $pid"
            else
                print_status "Process $pid stopped successfully"
                stopped_any=true
            fi
        else
            print_warning "Process $pid from PID file is not running"
        fi

        rm -f "$PID_FILE"
    fi

    # Method 2: Find and kill any remaining Python processes running app.py
    print_info "Checking for any remaining Python processes..."
    local remaining_pids=$(pgrep -f "python.*app.py" | tr '\n' ' ')

    if [ -n "$remaining_pids" ]; then
        print_warning "Found remaining Python processes: $remaining_pids"
        for pid in $remaining_pids; do
            if ps -p $pid > /dev/null 2>&1; then
                local port=$(lsof -p $pid -i -a 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2)
                print_info "Killing Python process $pid (port: ${port:-unknown})"
                kill -9 $pid 2>/dev/null
                stopped_any=true
            fi
        done
        sleep 2
    fi

    # Method 3: Check specific ports and kill processes using them
    for port in 3001 3000 8080 5000 8000; do
        local port_pid=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$port_pid" ]; then
            # Check if it's a Python process
            local cmd=$(ps -p $port_pid -o comm= 2>/dev/null)
            if [[ "$cmd" == "python"* ]]; then
                print_warning "Found Python process $port_pid still using port $port"
                kill -9 $port_pid 2>/dev/null
                stopped_any=true
            fi
        fi
    done

    # Final verification
    sleep 1
    local final_check=$(pgrep -f "python.*app.py" | tr '\n' ' ')
    if [ -n "$final_check" ]; then
        print_error "Some Python processes may still be running: $final_check"
        print_info "You may need to manually kill them:"
        for pid in $final_check; do
            local port=$(lsof -p $pid -i -a 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2)
            print_info "  kill -9 $pid  # (port: ${port:-unknown})"
        done
    else
        if [ "$stopped_any" = true ]; then
            print_status "✅ All Cognitrix processes stopped successfully"
        else
            print_info "No Cognitrix processes were running"
        fi
    fi
}

# Function to force stop all related processes
force_stop() {
    print_warning "🔥 Force stopping all Cognitrix processes..."

    # Kill all Python processes running app.py
    local pids=$(pgrep -f "python.*app.py")
    if [ -n "$pids" ]; then
        print_info "Force killing Python processes: $pids"
        for pid in $pids; do
            kill -9 $pid 2>/dev/null
        done
    fi

    # Kill processes on common ports
    for port in 3001 3000 8080 5000 8000 9000; do
        local port_pid=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$port_pid" ]; then
            local cmd=$(ps -p $port_pid -o comm= 2>/dev/null)
            if [[ "$cmd" == "python"* ]] || [[ "$cmd" == *"flask"* ]]; then
                print_info "Force killing process $port_pid on port $port"
                kill -9 $port_pid 2>/dev/null
            fi
        fi
    done

    # Clean up PID file
    rm -f "$PID_FILE"

    print_status "Force stop completed"
}

# Function to restart the application
restart_app() {
    local port=${1:-$DEFAULT_PORT}
    print_info "🔄 Restarting Cognitrix..."
    stop_app
    sleep 2
    start_app $port
}

# Function to check status
check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            local port=$(lsof -p $pid -i -a | grep LISTEN | awk '{print $9}' | cut -d: -f2)
            print_status "🟢 Cognitrix is running"
            print_info "PID: $pid"
            print_info "Port: $port"
            print_info "Access at: http://localhost:$port"

            # Find the most recent log file for this session
            local latest_log=$(ls -t "$LOG_DIR"/cognitrix_*.log 2>/dev/null | head -n1)
            if [ -n "$latest_log" ]; then
                print_info "Current log file: $latest_log"
                print_info "Recent log entries:"
                tail -5 "$latest_log" | while read line; do
                    echo "  $line"
                done
            fi
        else
            print_warning "PID file exists but process $pid is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_info "🔴 Cognitrix is not running"

        # Check for orphaned processes
        local pids=$(pgrep -f "python.*app.py")
        if [ -n "$pids" ]; then
            print_warning "Found orphaned processes: $pids"
            for pid in $pids; do
                local port=$(lsof -p $pid -i -a | grep LISTEN | awk '{print $9}' | cut -d: -f2)
                print_info "PID $pid running on port $port"
            done
        fi
    fi
}

# Function to show usage
show_usage() {
    echo "🧠 Cognitrix Process Manager"
    echo "Personal LLM Prompt Management System"
    echo ""
    echo "Usage: $0 [command] [port]"
    echo ""
    echo "Prerequisites:"
    echo "  - Virtual environment must be created: python3 -m venv venv"
    echo "  - Dependencies must be installed: pip install -r requirements.txt"
    echo "  - Virtual environment must be activated: source venv/bin/activate"
    echo ""
    echo "Commands:"
    echo "  start [port]  - Start Cognitrix (default port: $DEFAULT_PORT)"
    echo "  stop          - Stop Cognitrix gracefully"
    echo "  force-stop    - Force kill all Cognitrix processes"
    echo "  restart [port]- Restart Cognitrix"
    echo "  status        - Check if Cognitrix is running"
    echo "  logs          - Show recent logs (live tail)"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  source venv/bin/activate"
    echo "  $0 start      - Start on port $DEFAULT_PORT"
    echo "  $0 start 8080 - Start on port 8080"
    echo "  $0 stop       - Stop the service"
    echo "  $0 status     - Check status"
    echo ""
    echo "Quick Setup:"
    echo "  1. python3 -m venv venv"
    echo "  2. source venv/bin/activate"
    echo "  3. pip install -r requirements.txt"
    echo "  4. $0 start"
    echo ""
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log directory: $LOG_DIR"
    echo "  Current log: cognitrix_YYYYMMDD_HHMMSS.log"
    echo ""
    echo "Access: http://localhost:$DEFAULT_PORT"
}

# Function to show logs
show_logs() {
    # Find the most recent log file
    local latest_log=$(ls -t "$LOG_DIR"/cognitrix_*.log 2>/dev/null | head -n1)

    if [ -n "$latest_log" ]; then
        print_info "📋 Showing logs from: $latest_log (press Ctrl+C to exit)"
        echo ""
        tail -f "$latest_log"
    else
        print_warning "No log files found in: $LOG_DIR"
        print_info "Log files are created when you start the application with: $0 start"
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        start_app $2
        ;;
    stop)
        stop_app
        ;;
    force-stop)
        force_stop
        ;;
    restart)
        restart_app $2
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac