# CI/CD Guide for Legal Advisory System v5.0

## Overview

This guide explains the Continuous Integration and Continuous Deployment (CI/CD) system for the Legal Advisory System v5.0. The CI/CD pipeline ensures code quality, runs comprehensive tests, and automates deployment to Railway.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development Setup](#local-development-setup)
3. [Testing Locally](#testing-locally)
4. [Pre-commit Hooks](#pre-commit-hooks)
5. [GitHub Actions CI/CD Pipeline](#github-actions-cicd-pipeline)
6. [Deployment Process](#deployment-process)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For First-Time Setup

```bash
# 1. Clone repository (if not already done)
git clone <your-repo-url>
cd legal-advisory-v5

# 2. Run automated setup script
./setup_dev_environment.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run tests to verify
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/ tests/common_services/
```

**That's it!** Pre-commit hooks are now installed and will run automatically before each commit.

---

## Local Development Setup

### Manual Setup (Alternative to setup script)

If you prefer manual setup or the script doesn't work:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install production dependencies
pip install -r requirements.txt

# 3. Install development dependencies
pip install pytest pytest-cov pytest-asyncio pytest-timeout
pip install black isort ruff mypy
pip install pre-commit safety bandit

# 4. Install pre-commit hooks
pre-commit install
```

### Verify Installation

```bash
# Check Python version (requires 3.11+)
python3 --version

# Check pytest is installed
pytest --version

# Check pre-commit is installed
pre-commit --version
```

---

## Testing Locally

### Test Categories

The system has multiple test categories:

1. **Unit Tests** - Fast, isolated component tests
2. **Common Services Tests** - Tests for shared utilities
3. **Module Tests** - Tests for legal modules (Order 21, etc.)
4. **Conversation Tests** - Tests for conversation flow
5. **Emulator Tests** - Tests for AI/Database emulators
6. **Integration Tests** - End-to-end system tests
7. **Security Tests** - Security audit tests

### Running Tests

#### Run All Tests

```bash
PYTHONPATH=/home/claude/legal-advisory-v5 pytest
```

#### Run Fast Tests Only (Recommended for Development)

```bash
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/ tests/common_services/ -v
```

#### Run Specific Test Categories

```bash
# Unit tests only
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/

# Module tests only
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/modules/

# Integration tests only
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/integration/

# Security tests only
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/security/
```

#### Run Specific Test File

```bash
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/common_services/test_pattern_extractor.py -v
```

#### Run Specific Test Function

```bash
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/common_services/test_pattern_extractor.py::TestPatternExtractor::test_extract_amount_with_dollar_sign -v
```

### Test Coverage

#### Run Tests with Coverage

```bash
PYTHONPATH=/home/claude/legal-advisory-v5 pytest --cov=backend --cov-report=html
```

#### View Coverage Report

```bash
# Open HTML coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Pre-commit Hooks

Pre-commit hooks run automatically before each `git commit` to ensure code quality.

### What Gets Checked

1. **Code Formatting** (Black, isort)
2. **Linting** (Ruff)
3. **Type Checking** (MyPy)
4. **Security** (Bandit)
5. **Fast Tests** (Unit tests + common services tests)
6. **File Quality** (trailing whitespace, file endings, etc.)

### Running Pre-commit Hooks Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only (same as commit)
pre-commit run

# Run specific hook
pre-commit run black --all-files
pre-commit run pytest-local --all-files
```

### Bypassing Pre-commit Hooks (Use Sparingly!)

```bash
# Skip hooks for emergency fixes only
git commit --no-verify -m "Emergency fix"
```

**⚠️ Warning:** Only bypass hooks for critical production fixes. All bypassed commits will still be checked by GitHub Actions.

---

## GitHub Actions CI/CD Pipeline

### Pipeline Overview

The GitHub Actions pipeline runs automatically on:
- **Push to `main` or `develop` branches**
- **Pull requests to `main` or `develop` branches**

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Linting & Code Quality                │
│  • Black (formatting)  • isort (imports)  • Ruff (linting) │
│  • MyPy (type checking)                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       2. Unit Tests                          │
│  • Runs on Python 3.11 and 3.12                             │
│  • Tests: unit/, common_services/, hybrid_ai/, utils/      │
│  • Generates coverage report                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            3. Component Tests (Parallel)                     │
│  • Module Tests          • Conversation Tests                │
│  • Emulator Tests                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  4. Integration Tests                        │
│  • End-to-end system tests                                   │
│  • Performance tests                                         │
│  • Edge case tests                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    5. Security Audit                         │
│  • Security tests  • Safety check  • Bandit scan            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   6. Docker Build Test                       │
│  • Builds Docker image  • Tests health endpoint             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    7. Deploy to Railway                      │
│  • Only on main branch push                                  │
│  • Automatic deployment if all tests pass                   │
└─────────────────────────────────────────────────────────────┘
```

### Viewing Pipeline Results

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Select the workflow run
4. View detailed logs for each job

### Pipeline Configuration

Pipeline is configured in `.github/workflows/ci-cd.yml`

---

## Deployment Process

### Development Workflow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Developer  │─────▶│ Local Tests  │─────▶│  Git Commit │─────▶│ Pre-commit   │
│   Writes    │      │   (pytest)   │      │  (with msg) │      │ Hooks Run    │
│    Code     │      │              │      │             │      │              │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                                        │
                                                                        ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Deployed   │◀─────│   Railway    │◀─────│   GitHub    │◀─────│  Commit      │
│     to      │      │  Auto-Deploy │      │   Actions   │      │  Pushed to   │
│ Production  │      │              │      │  (All Jobs) │      │   GitHub     │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### Step-by-Step Deployment

1. **Write Code**
   ```bash
   # Edit your files
   vim backend/some_file.py
   ```

2. **Test Locally**
   ```bash
   # Run fast tests during development
   PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/unit/ tests/common_services/ -v
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks run automatically here
   ```

4. **Push to GitHub**
   ```bash
   git push origin main
   # GitHub Actions pipeline starts automatically
   ```

5. **Monitor Pipeline**
   - Go to GitHub Actions tab
   - Watch tests run (takes ~5-10 minutes)

6. **Automatic Deployment**
   - If all tests pass on `main` branch
   - Railway automatically deploys
   - Monitor at https://railway.app

### Branch Strategy

- **`main`** - Production branch (auto-deploys to Railway)
- **`develop`** - Development branch (tests run, no deploy)
- **Feature branches** - Create PR to `develop` or `main`

### Creating Pull Requests

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: implement new feature"

# Push feature branch
git push origin feature/new-feature

# Create PR on GitHub to main or develop
# Pipeline runs automatically on PR
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Fail Locally

**Error:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Always set PYTHONPATH
PYTHONPATH=/home/claude/legal-advisory-v5 pytest
```

#### 2. Pre-commit Hooks Fail

**Error:** `Hook failed`

**Solution:**
```bash
# See what failed
pre-commit run --all-files

# Fix formatting issues automatically
black backend/ tests/
isort backend/ tests/

# Re-commit
git add .
git commit -m "your message"
```

#### 3. Type Checking Fails

**Error:** MyPy type errors

**Solution:**
```bash
# Check types manually
mypy backend/ --ignore-missing-imports

# Add type ignore comments for third-party libraries
# type: ignore
```

#### 4. GitHub Actions Fails But Local Tests Pass

**Possible causes:**
- Environment differences (Python version)
- Missing dependencies in requirements.txt
- Different PYTHONPATH

**Solution:**
- Check GitHub Actions logs carefully
- Ensure requirements.txt is up-to-date
- Test with multiple Python versions locally

#### 5. Coverage Too Low

**Error:** Coverage below threshold

**Solution:**
```bash
# Generate HTML coverage report to see gaps
PYTHONPATH=/home/claude/legal-advisory-v5 pytest --cov=backend --cov-report=html

# Open report
open htmlcov/index.html

# Add tests for uncovered code
```

### Getting Help

1. **Check CI/CD logs** - Most detailed error information
2. **Run tests locally** - Reproduce issues
3. **Check pytest.ini** - Configuration issues
4. **Check .pre-commit-config.yaml** - Hook configuration

---

## Best Practices

### 1. Test-Driven Development (TDD)

```bash
# 1. Write test first
vim tests/common_services/test_new_feature.py

# 2. Run test (should fail)
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/common_services/test_new_feature.py

# 3. Implement feature
vim backend/common_services/new_feature.py

# 4. Run test again (should pass)
PYTHONPATH=/home/claude/legal-advisory-v5 pytest tests/common_services/test_new_feature.py
```

### 2. Small, Frequent Commits

```bash
# Good - Small, focused commit
git commit -m "feat: add court level extraction to PatternExtractor"

# Bad - Large, unfocused commit
git commit -m "fix stuff"
```

### 3. Meaningful Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

### 4. Keep Tests Fast

- Unit tests should run in < 1 second each
- Use mocks for external services
- Use emulators for testing without API keys

### 5. Monitor Coverage

```bash
# Aim for >80% coverage on critical code
PYTHONPATH=/home/claude/legal-advisory-v5 pytest --cov=backend --cov-report=term-missing
```

---

## Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **pre-commit documentation**: https://pre-commit.com/
- **GitHub Actions documentation**: https://docs.github.com/en/actions
- **Railway documentation**: https://docs.railway.app/

---

## Summary

✅ **What You Have Now:**

1. Comprehensive test suite covering all components
2. Automated pre-commit hooks for local quality checks
3. GitHub Actions CI/CD pipeline with 8 stages
4. Automatic deployment to Railway on main branch
5. Code coverage tracking and reporting
6. Security scanning and vulnerability detection
7. Multi-version Python testing (3.11, 3.12)
8. Docker build verification

✅ **What This Means:**

- **Quality Guarantee**: Bad code can't reach production
- **Fast Feedback**: Find issues in seconds, not hours
- **Confidence**: Deploy knowing tests passed
- **Documentation**: Tests serve as living documentation
- **Security**: Automated vulnerability scanning

---

**Happy testing! 🚀**
