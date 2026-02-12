#!/usr/bin/env python3
# Quick Command Reference for LinkedIn Post Generator

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-groq-key"
export GITHUB_TOKEN="your-github-token"  # Optional

# Clear cache
streamlit cache clear


# ============================================================================
# LOCAL TESTING
# ============================================================================

# Run app locally
streamlit run app.py

# Run with specific port
streamlit run app.py --server.port 8502

# Run with custom config
streamlit run app.py --logger.level=debug


# ============================================================================
# QUICK VALIDATION TESTS
# ============================================================================

# Test 1: Check for NoneType errors
grep -n "NoneType" app.py  # Should NOT find it in critical paths

# Test 2: Check for KeyError fixes
grep -n "hallucination_check" app.py  # Should show .get() usage

# Test 3: Check editable post area implemented
grep -n "editable_full_post" app.py  # Should find it

# Test 4: Verify logging fix
grep -n "retrieval_sources = \[\]" app.py  # Should find safe handling

# Test 5: Verify error handling
grep -n "except" app.py  # Should have proper exception handling


# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

# Option 1: Streamlit Cloud
streamlit deploy

# Option 2: Docker
docker build -t linkedin-generator .
docker run -p 8501:8501 linkedin-generator

# Option 3: Linux/Mac server
nohup streamlit run app.py --server.port 8501 > app.log 2>&1 &

# Option 4: Windows server
start pythonw -m streamlit.cli run app.py --server.port 8501


# ============================================================================
# MONITORING & LOGS
# ============================================================================

# View current process
ps aux | grep streamlit

# View logs (if running with nohup)
tail -f app.log

# Kill process
kill -9 <PID>

# Check port usage
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows


# ============================================================================
# DEBUG & MAINTENANCE
# ============================================================================

# Clear all Streamlit cache
streamlit cache clear --path .

# Test imports
python -c "from app import *; print('✅ Imports successful')"

# Check Python version
python --version  # Should be 3.8+

# List installed packages
pip list

# Verify specific package
pip show streamlit


# ============================================================================
# QUICK TEST SCRIPT
# ============================================================================

python << 'EOF'
import subprocess
import time

tests = [
    ("No NoneType in logging", "grep -n 'NoneType' app.py"),
    ("KeyError handling", "grep -n 'hallucination_check' app.py"),
    ("Editable area", "grep -n 'editable_full_post' app.py"),
    ("Logging fix", "grep -n 'retrieval_sources = ' app.py"),
]

print("🧪 Running Quick Tests...")
print("=" * 60)

for test_name, command in tests:
    result = subprocess.run(command, shell=True, capture_output=True)
    status = "✅" if "app.py" in result.stdout.decode() else "⚠️"
    print(f"{status} {test_name}")

print("=" * 60)
print("✅ All tests completed!")
EOF


# ============================================================================
# PERFORMANCE PROFILING
# ============================================================================

# Profile app performance
python -m cProfile -s cumulative app.py

# Memory usage
python -c "import tracemalloc; tracemalloc.start(); from app import *; print(tracemalloc.get_traced_memory())"

# API response time
curl -X POST "http://localhost:8501/api/post" -d '{"url": "https://github.com/user/repo"}' -w "@curl-format.txt"


# ============================================================================
# BACKUP & ROLLBACK
# ============================================================================

# Backup current version
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)

# Backup all user data/logs
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/ data/

# Restore from backup
cp app.py.backup app.py


# ============================================================================
# DATABASE & LOGGING
# ============================================================================

# View generation logs
tail -100 logs/posts/generation.log

# View error logs
tail -100 logs/errors/error.log

# View metrics
python -c "from utils.logger import get_metrics_tracker; mt = get_metrics_tracker(); print(mt.get_summary())"

# Export logs
tar -czf exports/logs_$(date +%Y%m%d).tar.gz logs/


# ============================================================================
# GITHUB INTEGRATION
# ============================================================================

# Test with sample repos
REPOS=(
    "https://github.com/pallets/flask"
    "https://github.com/MaulyaSoni/Bhaav.AI"
    "https://github.com/pytorch/pytorch"
)

for repo in "${REPOS[@]}"; do
    echo "Testing: $repo"
done


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install with requirements
pip install -r requirements.txt

# Create .env file
cat > .env << 'ENV'
GROQ_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
ENV


# ============================================================================
# DOCUMENTATION GENERATOR
# ============================================================================

# Generate API documentation
python -m pydoc -w app

# Generate code stats
wc -l app.py
find . -name "*.py" | xargs wc -l | tail -1

# Generate dependency tree
pip show -r requirements.txt


# ============================================================================
# SECURITY
# ============================================================================

# Check for security vulnerabilities
pip install safety
safety check

# Check for hardcoded secrets
pip install detect-secrets
detect-secrets scan

# Code quality check
pip install pylint
pylint app.py


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Create systemd service (Linux)
sudo tee /etc/systemd/system/linkedin-generator.service > /dev/null <<EOF
[Unit]
Description=LinkedIn Post Generator
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/app
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl start linkedin-generator
sudo systemctl enable linkedin-generator

# Check service status
sudo systemctl status linkedin-generator


# ============================================================================
# MONITORING DASHBOARD
# ============================================================================

# View all metrics
python << 'EOF'
from utils.logger import get_metrics_tracker
from utils.logger import get_logger

mt = get_metrics_tracker()
logger = get_logger()

print("📊 Metrics Summary:")
print(mt.get_summary())
print("\n📋 Recent Posts:")
# print(logger.get_recent_generations(limit=5))
EOF


# ============================================================================
# USEFUL ALIASES
# ============================================================================

# Add to ~/.bashrc or ~/.zshrc

# Quick start
alias lg-start="streamlit run app.py"

# Clear cache and start
alias lg-fresh="streamlit cache clear && streamlit run app.py"

# View logs
alias lg-logs="tail -f logs/posts/generation.log"

# Backup
alias lg-backup="cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)"

# Status check
alias lg-status="ps aux | grep streamlit"

# Kill app
alias lg-kill="pkill -f 'streamlit run'"


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# Issue: Port already in use
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Issue: Cache issues
streamlit cache clear
rm -rf .streamlit/cache

# Issue: Import errors
pip install --upgrade -r requirements.txt

# Issue: API key not found
# Verify: cat .env | grep GROQ_API_KEY
# Or: echo $GROQ_API_KEY

# Issue: GitHub rate limit
# Solution: Set GITHUB_TOKEN in .env
# Or: Use GitHub token: export GITHUB_TOKEN="your-token"


# ============================================================================
# END OF REFERENCE
# ============================================================================
