#!/bin/bash
# Quick setup script for Speech-to-Task Prompt-Tuning MVP

echo "================================================"
echo "Speech-to-Task Prompt-Tuning MVP - Setup"
echo "================================================"

# Check Python version
echo -e "\n1. Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

# Create virtual environment
echo -e "\n2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo -e "\n3. Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "\n4. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate sample data
echo -e "\n5. Generating sample data..."
python -m src.cli generate-data --output data/simulated_commands.json --count 100

echo -e "\n================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run baseline evaluation:"
echo "     python -m src.cli evaluate --mode baseline --data data/simulated_commands.json"
echo ""
echo "  3. Optimize prompts:"
echo "     python -m src.cli optimize --data data/simulated_commands.json --output results/"
echo ""
echo "  4. Try the demo:"
echo "     python -m src.cli demo --input \"Set timer for 20 minutes\" --speaker parent"
echo ""
echo "For more information, see README.md"
echo "================================================"
