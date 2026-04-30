# LinkedIn Post Generator v3.0 - Setup Guide

## Quick Start (5 minutes)

### Option 1: Automated Setup

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# IMPORTANT: Edit .env and add your API keys:
# - GROQ_API_KEY (get from https://console.groq.com)
# - OPENAI_API_KEY (get from https://platform.openai.com)
# - SECRET_KEY (generate a random string)
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment is already configured in .env.local
```

#### 3. Database Setup

```bash
# Option A: Using Docker (easiest)
docker-compose up -d postgres redis

# Option B: Using local installations
# - Install PostgreSQL 15+
# - Install Redis 7+
# - Create database: createdb linkedin_generator
```

#### 4. Start the Application

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Configuration

### Required API Keys

#### Groq API (Fast LLM inference)
1. Go to https://console.groq.com
2. Sign up for free account
3. Create API key
4. Add to `backend/.env`: `GROQ_API_KEY=your_key`

#### OpenAI API (Optional, for higher quality)
1. Go to https://platform.openai.com
2. Sign up and add credits
3. Create API key
4. Add to `backend/.env`: `OPENAI_API_KEY=your_key`

### Database Configuration

Default PostgreSQL URL in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_generator
```

If using different credentials, update accordingly.

### Redis Configuration

Default Redis URL in `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

## Docker Setup (Alternative)

If you prefer Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running
- Verify database credentials in `.env`
- Ensure all Python dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Check Node.js version (need 18+): `node --version`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if backend is running at http://localhost:8000

### API errors
- Check backend logs for errors
- Verify API keys are set correctly in `.env`
- Test API at http://localhost:8000/docs

### Database errors
- Create the database: `createdb linkedin_generator`
- Check PostgreSQL is running: `pg_isready`
- Verify connection string in `.env`

## Testing the Setup

1. **Register a user**:
   - Go to http://localhost:3000/auth/register
   - Create an account

2. **Generate a post**:
   - Login at http://localhost:3000/auth/login
   - Click "Generate New Post"
   - Enter a topic and click generate

3. **View API docs**:
   - Visit http://localhost:8000/docs
   - Test endpoints directly

## Next Steps

- [ ] Configure your API keys
- [ ] Set up PostgreSQL database
- [ ] Set up Redis cache
- [ ] Create your first user account
- [ ] Generate your first AI-powered LinkedIn post!

## Getting Help

- Check the documentation in the parent directory
- Review API docs at http://localhost:8000/docs
- Check backend logs for error messages

---

Ready to build amazing LinkedIn content! 🚀
