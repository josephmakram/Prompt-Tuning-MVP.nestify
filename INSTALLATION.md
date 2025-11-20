# Installation & Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment support (venv)

## Quick Installation

### 1. Navigate to Project Directory

```bash
cd prompt-tuning-mvp
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- dspy-ai (>= 2.0)
- numpy (>= 1.24.0)
- pandas (>= 2.0.0)
- scikit-learn (>= 1.3.0)
- pydantic (>= 2.0.0)
- pytest (>= 7.4.0)
- rich (>= 13.0.0)

### 4. Verify Installation

```bash
# Test data generator
python3 -m src.data.generator

# Run tests
pytest tests/ -v

# Show help
python3 -m src.cli --help
```

## Running the Demo

Once installed, run the complete demo:

```bash
python3 run_demo.py
```

This will:
1. Generate simulated dataset (100 speech commands)
2. Evaluate baseline pipeline
3. Optimize prompts using DSPy
4. Evaluate optimized pipeline
5. Show comparison results
6. Run example predictions

Expected runtime: 1-2 minutes

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Install dependencies
```

### Issue: Permission Denied

**Solution:** Make run_demo.py executable:
```bash
chmod +x run_demo.py
```

### Issue: Import Errors

**Solution:** Run from project root directory:
```bash
cd prompt-tuning-mvp
python3 run_demo.py
```

### Issue: DSPy Errors

**Solution:** Ensure you have dspy-ai >= 2.0:
```bash
pip install --upgrade dspy-ai
```

## Using the CLI

After installation, you can use various CLI commands:

```bash
# Generate custom dataset
python3 -m src.cli generate-data --count 150

# Evaluate on test set
python3 -m src.cli evaluate --data data/simulated_commands.json --split test

# Run optimization
python3 -m src.cli optimize --data data/simulated_commands.json

# Try a demo command
python3 -m src.cli demo --input "Set timer for 30 minutes" --speaker parent
```

## Deactivating Virtual Environment

When done:

```bash
deactivate
```

## Uninstallation

To completely remove:

```bash
# Deactivate venv if active
deactivate

# Remove virtual environment
rm -rf venv

# Remove generated data (optional)
rm -rf data/*.json results/*.json
```

## Development Setup

For development with auto-reload and debugging:

```bash
# Install development dependencies
pip install pytest pytest-cov ipython

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Next Steps

After installation:
1. Read README.md for project overview
2. Run `python3 run_demo.py` to see it in action
3. Explore the code in src/
4. Try different CLI commands
5. Run tests to verify everything works

Enjoy optimizing prompts!
