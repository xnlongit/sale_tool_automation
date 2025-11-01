#!/bin/bash
# Script chạy ER Sports Automation trên Linux với xử lý lỗi X11

set -e

echo "=========================================="
echo "ER Sports Automation - Linux Launcher"
echo "=========================================="
echo ""

# Check if running in headless environment
if [ -z "$DISPLAY" ]; then
    echo "Warning: DISPLAY not set. Trying to use xvfb..."
    
    # Check if xvfb is available
    if command -v xvfb-run &> /dev/null; then
        echo "Using xvfb to run application..."
        echo ""
        xvfb-run -a python3 src/main.py
    else
        echo "Error: DISPLAY not set and xvfb not found."
        echo ""
        echo "Solutions:"
        echo "1. Set DISPLAY: export DISPLAY=:0.0"
        echo "2. Install xvfb: sudo apt-get install xvfb"
        echo "3. Use X11 forwarding: ssh -X user@host"
        echo ""
        exit 1
    fi
else
    echo "DISPLAY is set to: $DISPLAY"
    echo ""
    
    # Set X11 environment variables to fix rendering issues
    export TK_SILENCE_DEPRECATION=1
    export XLIB_SKIP_ARGB_VISUALS=1
    export MESA_GL_VERSION_OVERRIDE=3.3
    
    # Disable some problematic X11 features
    export QT_X11_NO_MITSHM=1
    
    # Run the application
    # Note: X11 rendering errors are handled in Python code
    python3 src/main.py
fi

