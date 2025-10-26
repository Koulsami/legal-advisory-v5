#!/bin/bash
# Setup Development Environment for Legal Advisory System v5.0
# This script installs all development dependencies and sets up pre-commit hooks

set -e  # Exit on error

echo "=================================================="
echo "Legal Advisory System v5.0"
echo "Development Environment Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Production dependencies installed"
echo ""

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install pytest pytest-cov pytest-asyncio pytest-timeout > /dev/null 2>&1
pip install black isort ruff mypy > /dev/null 2>&1
pip install pre-commit > /dev/null 2>&1
pip install safety bandit > /dev/null 2>&1
echo "✅ Development dependencies installed"
echo ""

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install > /dev/null 2>&1
echo "✅ Pre-commit hooks installed"
echo ""

# Run initial tests to verify setup
echo "🧪 Running initial test verification..."
echo "   (This may take a minute...)"
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/test_configuration.py -v --tb=short
echo "✅ Initial tests passed"
echo ""

# Print summary
echo "=================================================="
echo "✅ Development Environment Setup Complete!"
echo "=================================================="
echo ""
echo "📚 What was installed:"
echo "   • Python dependencies (production + dev)"
echo "   • Testing tools (pytest, coverage)"
echo "   • Code quality tools (black, ruff, mypy)"
echo "   • Pre-commit hooks"
echo "   • Security tools (bandit, safety)"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. Run all tests:"
echo "   PYTHONPATH=/home/claude/legal-advisory-v5 pytest"
echo ""
echo "3. Run fast tests only (unit + common_services):"
echo "   PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/ tests/common_services/"
echo ""
echo "4. Run with coverage:"
echo "   PYTHONPATH=/home/claude/legal-advisory-v5 pytest --cov=backend --cov-report=html"
echo ""
echo "5. Format code:"
echo "   black backend/ tests/"
echo "   isort backend/ tests/"
echo ""
echo "6. Type check:"
echo "   mypy backend/ --ignore-missing-imports"
echo ""
echo "7. Pre-commit hooks will run automatically on git commit"
echo "   Or run manually: pre-commit run --all-files"
echo ""
echo "=================================================="
echo "Happy coding! 🎉"
echo "=================================================="
