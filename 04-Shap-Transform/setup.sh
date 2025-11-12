#!/bin/bash

# Insurance Claim AI Agent - Setup Script

echo "========================================================================"
echo "  Insurance Claim AI Agent - Setup"
echo "========================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found"
echo ""

# Create virtual environment (optional but recommended)
echo "Do you want to create a virtual environment? (recommended) [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate  (Linux/Mac)"
    echo "  venv\\Scripts\\activate     (Windows)"
    echo ""
fi

# Install dependencies
echo "Do you want to install dependencies now? [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Installing dependencies..."
    
    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        pip install -r requirements.txt
    else
        echo "Installing with --break-system-packages flag..."
        pip install --break-system-packages -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ Dependencies installed successfully"
    else
        echo "⚠️ Some dependencies may have failed to install"
        echo "You can still run the lightweight demo without dependencies"
    fi
else
    echo "Skipping dependency installation"
    echo "You can run the lightweight demo without dependencies"
fi

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "========================================================================"
echo ""
echo "Quick Start:"
echo ""
echo "1. Run the lightweight demo (no dependencies needed):"
echo "   python demo_lightweight.py"
echo ""
echo "2. Run the full demo (requires dependencies):"
echo "   python main.py"
echo ""
echo "3. Run tests:"
echo "   python test_agent.py"
echo ""
echo "4. Start API server:"
echo "   python api_server.py"
echo ""
echo "For more information, see:"
echo "  - README.md (comprehensive documentation)"
echo "  - QUICKSTART.md (quick start guide)"
echo "  - CHANGELOG.md (version history)"
echo ""
echo "========================================================================"
