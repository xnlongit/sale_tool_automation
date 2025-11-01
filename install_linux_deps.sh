#!/bin/bash
# Script cài đặt dependencies cho ER Sports Automation trên Linux
# Hỗ trợ Ubuntu/Debian và CentOS/RHEL

set -e

echo "=========================================="
echo "ER Sports Automation - Linux Dependencies"
echo "=========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "Không thể detect OS. Vui lòng cài đặt thủ công."
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Function for Ubuntu/Debian
install_debian() {
    echo "Installing dependencies for Debian/Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-dev python3-pip
    sudo apt-get install -y xfonts-base xfonts-75dpi
    sudo apt-get install -y libx11-dev libxext-dev libxrender-dev
    sudo apt-get install -y build-essential
    sudo apt-get install -y xvfb  # Optional: for headless servers
    echo "✓ Debian/Ubuntu dependencies installed"
}

# Function for CentOS/RHEL
install_centos() {
    echo "Installing dependencies for CentOS/RHEL..."
    sudo yum install -y python3-tkinter python3-devel python3-pip
    sudo yum install -y xorg-x11-fonts-base xorg-x11-fonts-75dpi
    sudo yum install -y libX11-devel libXext-devel libXrender-devel
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y xorg-x11-server-Xvfb  # Optional: for headless servers
    echo "✓ CentOS/RHEL dependencies installed"
}

# Install based on OS
case "$OS" in
    ubuntu|debian)
        install_debian
        ;;
    centos|rhel|fedora)
        install_centos
        ;;
    *)
        echo "OS không được hỗ trợ tự động: $OS"
        echo "Vui lòng cài đặt thủ công theo BUILD_INSTRUCTIONS.md"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Installing Python packages..."
echo "=========================================="

# Install Python packages
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "✓ Installation completed!"
echo "=========================================="
echo ""
echo "Để chạy ứng dụng:"
echo "  python3 src/main.py"
echo ""
echo "Nếu gặp lỗi X11, thử:"
echo "  export DISPLAY=:0.0"
echo "  export XLIB_SKIP_ARGB_VISUALS=1"
echo "  python3 src/main.py"
echo ""
echo "Hoặc với xvfb (headless):"
echo "  xvfb-run -a python src/main.py"
echo ""

