# 🔐 Demo Credentials & Testing Guide

## 📝 Quick Demo Account

Since you're using this for personal/demo purposes, here are pre-configured test credentials:

### Test Account (Create via Registration)

**Option 1: Manual Registration**
1. Go to http://localhost:3000/auth/register
2. Create an account with any email/password
3. Example:
   - **Email:** demo@example.com
   - **Password:** demo123456
   - **Name:** Demo User

**Option 2: Use These Credentials After Registration**
Once you register, use those credentials to login.

## 🧪 Testing the Application

### Step-by-Step Test Flow

#### 1. **Register Account**
```
URL: http://localhost:3000/auth/register
Fields:
- Name: Your Name
- Email: your@email.com
- Password: yourpassword (min 8 chars)
```

#### 2. **Login**
```
URL: http://localhost:3000/auth/login
Enter your credentials
```

#### 3. **Generate a Post**
```
URL: http://localhost:3000/dashboard/generate
Fill in:
- Topic: "AI in 2026" (or any topic)
- Tone: "professional"
- Target Audience: "tech professionals"
- Context: "Share insights about AI trends"
Click: "Generate Post"
```

#### 4. **View Results**
You'll see:
- Generated post content
- Quality score (0-100)
- Engagement prediction
- Suggested hashtags
- Generated image (if enabled)

## 🔧 API Testing (Direct Backend)

### Using API Documentation
```
URL: http://localhost:8000/docs
This is the Swagger UI - test all endpoints directly!
```

### Test Endpoints

#### 1. Register User
```http
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
  "name": "Demo User",
  "email": "demo@example.com",
  "password": "demo123456"
}
```

#### 2. Login
```http
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "email": "demo@example.com",
  "password": "demo123456"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### 3. Generate Post
```http
POST http://localhost:8000/api/posts/generate
Authorization: Bearer {your_token}
Content-Type: application/json

{
  "topic": "AI in 2026",
  "tone": "professional",
  "target_audience": "tech professionals",
  "context": "Share insights about AI trends"
}
```

## 📊 Demo Data

### Sample Topics to Try

1. **Technology:**
   - Topic: "The Future of AI in Software Development"
   - Tone: "thought_leader"
   - Audience: "developers and tech leaders"

2. **Business:**
   - Topic: "Remote Work Best Practices"
   - Tone: "professional"
   - Audience: "business professionals"

3. **Personal Growth:**
   - Topic: "Lessons Learned from 10 Years in Tech"
   - Tone: "personal"
   - Audience: "young professionals"

4. **Industry Insights:**
   - Topic: "Why Every Company Needs a Digital Strategy"
   - Tone: "analytical"
   - Audience: "executives and decision makers"

## 🎯 Feature Checklist for Demo

- ✅ User Registration
- ✅ User Login
- ✅ JWT Authentication
- ✅ Post Generation (AI-powered)
- ✅ Quality Scoring
- ✅ Multiple Post Variants
- ✅ Fact-Checking
- ✅ Hashtag Suggestions
- ✅ Engagement Prediction
- ✅ Image Generation (placeholder mode)
- ✅ Post History
- ✅ Analytics Dashboard
- ✅ Copy to Clipboard

## 🐛 Common Issues & Solutions

### Issue: "Database connection refused"
**Solution:** Already fixed! Using SQLite now, no server needed.

### Issue: "Invalid API key"
**Solution:** Your Groq API key is configured. If it expires, get a new one at https://console.groq.com

### Issue: "Post generation fails"
**Solutions:**
1. Check Groq API key is valid
2. Try a simpler topic
3. Check backend logs in terminal

### Issue: "Frontend shows 404"
**Solution:** Frontend is running on http://localhost:3000 (not the old URL)

## 📝 Database Location

**SQLite Database:** `backend/linkedin_generator.db`
- Auto-created on first run
- Stores users, posts, profiles
- Easy to backup/delete

**To Reset Database:**
```powershell
cd backend
Remove-Item linkedin_generator.db
# Restart backend - new DB will be created
```

## 🚀 Quick Commands

### Start Everything
```powershell
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Check Status
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 💡 Pro Tips

1. **Test with Swagger first:** Use http://localhost:8000/docs to test backend directly
2. **Check terminal logs:** See real-time backend processing
3. **Try different tones:** Each tone generates very different content
4. **Use specific topics:** More specific = better generated content
5. **Quality score > 70:** Anything above 70 is good quality

---

**Ready to Demo!** 🎉

Visit http://localhost:3000 and start creating LinkedIn posts!
