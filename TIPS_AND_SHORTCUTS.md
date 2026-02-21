# ⌨️ TIPS & KEYBOARD SHORTCUTS

## 🎨 UI Navigation Tips

### 1. Theme Switching
- **Location:** Top of sidebar
- **Action:** Click "🌙 Dark Mode" toggle
- **Effect:** Instant theme switch with page reload
- **Tip:** Try both themes to see gradient changes

### 2. Mode Selection
- **Location:** Main content area, top section
- **Action:** Click mode card OR "Select [Mode]" button
- **Modes:** Simple (fast), Advanced (RAG-powered)
- **Tip:** Simple mode = 1-3s, Advanced mode = 8-15s

### 3. Sidebar Sections
- **Scroll down** to see all sections:
  - Theme toggle
  - LinkedIn Tips (5 cards)
  - System Status
  - Account Info
  - Chat History
- **Tip:** Click expander arrows to collapse/expand

### 4. Post Type Selector
- **Radio buttons:** Choose from 4 types
  - 🚀 SIMPLE Topic
  - 📊 ADVANCED GitHub
  - 🏆 HACKATHON Project
  - 🤖 AGENTIC Studio
- **Tip:** Each type has different input fields

---

## 🔘 Button Quick Reference

### Generation Buttons

| Button                    | Location         | Function                              |
|---------------------------|------------------|---------------------------------------|
| **🚀 Generate Post**      | Main area        | Starts generation process             |
| **✨ Generate Hackathon** | Hackathon form   | Creates hackathon-specific post       |
| **🚀 Generate w/ Agents** | Agentic Studio   | Starts 6-agent pipeline               |

### Action Buttons (After Generation)

| Button               | Color Combo        | Function                              |
|----------------------|--------------------|---------------------------------------|
| **📋 Copy Full**     | Red-White (Light)  | Shows full post + hashtags in code    |
| **📄 Copy Post**     | Black-White (Light)| Shows post text only                  |
| **#️⃣ Copy Hashtags**| Blue-Cyan (Light)  | Shows hashtags only                   |
| **⬇️ Download**      | White-Red (Light)  | Downloads as .txt file                |
| **🔄 Regenerate**    | Primary gradient   | Clears and starts new generation      |

**Dark Mode Colors:** Yellow-Black, Cyan-Black, Green-Black, White-Red

### Agentic Variant Buttons (Per Variant)

| Button               | Function                              |
|----------------------|---------------------------------------|
| **📋 Copy**          | Shows variant text                    |
| **⬇️ Download**      | Downloads variant as .txt             |
| **📤 Post Now**      | Posts to LinkedIn immediately         |
| **⏰ Schedule**      | Opens scheduler for delayed posting   |

---

## ⌨️ Keyboard Shortcuts

### Streamlit Defaults (Still Work)

| Shortcut             | Function                              |
|----------------------|---------------------------------------|
| **Ctrl + R**         | Rerun the app                         |
| **Ctrl + Shift + R** | Clear cache and rerun                 |
| **?**                | Show keyboard shortcuts (Streamlit)   |

### Navigation

| Action               | Shortcut                              |
|----------------------|---------------------------------------|
| **Focus input**      | Click or Tab to field                 |
| **Submit form**      | Enter (when in text input)            |
| **Toggle sidebar**   | Click hamburger menu (mobile)         |

### Copy Actions

| Action               | How To                                |
|----------------------|---------------------------------------|
| **Copy post**        | Click button → Copy from code block   |
| **Select all**       | Ctrl+A (in text area)                 |
| **Copy text**        | Ctrl+C (standard)                     |
| **Paste text**       | Ctrl+V (standard)                     |

---

## 💡 Pro Tips

### 1. Quick Copy Workflow
```
1. Click "📋 Copy Full Post"
2. See code block appear
3. Click Streamlit's copy button (top-right of code block)
4. OR manually select all (Ctrl+A) and copy (Ctrl+C)
5. Paste into LinkedIn (Ctrl+V)
```

### 2. Theme Preference
```
Light Mode: Better for daytime, well-lit rooms
Dark Mode:  Better for night, dark rooms, reduces eye strain

Gradient Changes:
Light → Blue/Red/Black (professional)
Dark  → Yellow/Cyan/Green (vibrant)
```

### 3. Quality Improvements
```
In "Advanced Options" expander:
✓ Enforce Specificity — Removes vague phrases
✓ Show Quality Score  — Displays 5 metrics
✓ Generate Hooks      — Creates 3 hook options
✓ Verify Claims       — Grounds in context (Advanced mode only)
```

### 4. Best Post Type for Each Use Case

| Use Case                          | Best Mode         |
|-----------------------------------|-------------------|
| **Quick idea → post**             | SIMPLE Topic      |
| **GitHub repo → post**            | ADVANCED GitHub   |
| **Contest/project story**         | HACKATHON Project |
| **Multi-input + 3 variants**      | AGENTIC Studio    |

### 5. Agentic Studio Best Practices
```
1. Provide at least ONE input (text/image/doc/URL)
2. Paste 3-10 past posts for better brand voice alignment
3. Choose appropriate tone & audience
4. All 6 agents will run (~15-30s total)
5. Compare 3 variants and pick your favorite
6. Use inline buttons (Copy/Post/Schedule per variant)
```

### 6. Download vs Copy
```
Copy:     Quick paste into LinkedIn/Twitter/etc.
Download: Save for later, backup, sharing with team

Tip: Download if you'll revise later in a text editor
```

### 7. Regenerate vs New Post
```
Regenerate:  Same inputs, try again (if not satisfied)
New Post:    Clear everything, start from scratch

Tip: Use Regenerate if post was close but needs a retry
```

### 8. Chat History Tracking
```
- Auto-saves every successful generation
- Shows last 5 posts
- Displays: Topic (first 40 chars) + Time (HH:MM)
- Persists during session only (clears on page refresh)

Tip: Keep track of what you've generated today
```

### 9. Account Stats Tracking
```
Posts Generated: Total all-time successful posts
Session Count:   Current session generation attempts

Tip: Useful for tracking your usage patterns
```

### 10. Mobile vs Desktop
```
Desktop: Full layout, sidebar visible
Mobile:  Collapsed sidebar (hamburger menu)

Tip: Toggle dark mode to see if mobile readability improves
```

---

## 🎨 Color Customization (Advanced)

### How to Change Theme Colors

**File:** `ui/styles.py`

**Classes:** `ThemeLight`, `ThemeDark`

**Example:**
```python
class ThemeLight:
    PRIMARY = "#1D4ED8"  # Change this to your brand color
    GRADIENT_START = "#1D4ED8"  # Gradient color 1
    GRADIENT_MID = "#DC2626"     # Gradient color 2
    GRADIENT_END = "#111827"     # Gradient color 3
```

**After editing:**
1. Save the file
2. Rerun the app (Ctrl+R)

---

## 🔧 Troubleshooting

### Issue: Buttons not responding
**Solution:**
- Make sure post was generated first
- Check browser console (F12) for errors
- Try refreshing page (Ctrl+R)

### Issue: Dark mode toggle not working
**Solution:**
- Click toggle and wait 2-3 seconds
- Page should auto-reload
- If not, manually refresh (Ctrl+R)

### Issue: Fonts look wrong
**Solution:**
- Check internet connection (Google Fonts CDN)
- Clear browser cache (Ctrl+Shift+Del)
- Try different browser (Chrome recommended)

### Issue: Gradients not showing
**Solution:**
- Update browser to latest version
- Try Chrome/Firefox/Edge (Safari may have issues)
- Check if browser supports `-webkit-background-clip`

### Issue: Loading animation stuck
**Solution:**
- Wait 60 seconds (some generations are slow)
- Check API key is valid (GROQ_API_KEY)
- Check console for errors (F12)
- Refresh page and retry

### Issue: Copy buttons don't copy
**Solution:**
- Buttons show code blocks (not auto-copy)
- Use Streamlit's copy button (top-right of code block)
- Or manually select text and Ctrl+C

---

## 🎯 Best Practices

### 1. Optimal Workflow
```
1. Select post type
2. Fill in inputs
3. Adjust tone/audience
4. Check "Advanced Options" if needed
5. Click Generate
6. Review post
7. Click "Copy Full Post"
8. Paste into LinkedIn
9. Schedule or post immediately
```

### 2. Quality Checklist
```
Before posting:
☐ Check grammar/spelling
☐ Verify facts (if claims are made)
☐ Review hashtags (are they relevant?)
☐ Check tone matches audience
☐ Ensure hook grabs attention
☐ Add call-to-action if needed
```

### 3. Theme Selection
```
Light Mode → Use for:
- Daytime work
- Well-lit offices
- Screenshot sharing (looks professional)

Dark Mode → Use for:
- Night work
- Dark rooms
- Eye strain reduction
- Personal preference
```

### 4. Mode Selection Guide
```
Simple Mode → When you:
- Need a quick post (1-3s)
- Have a general topic
- Don't need deep context

Advanced Mode → When you:
- Have a GitHub repo
- Need RAG-powered quality
- Want context-aware posts
- Accept 8-15s wait time

Hackathon Mode → When you:
- Participated in a competition
- Have a project story to share
- Want structured narrative

Agentic Studio → When you:
- Have multi-modal input (text/images/docs)
- Want 3 different variants
- Need brand voice alignment
- Want engagement predictions
```

---

## 🎊 Hidden Features

### 1. Quality Score Details
When enabled, shows 5 metrics:
- **Clarity:** How clear the message is
- **Specificity:** Avoids vague language
- **Engagement:** Predicted social engagement
- **Credibility:** Trustworthiness
- **Actionability:** Provides value

### 2. Hook Options
When enabled (Simple mode only), generates 3 hooks:
- **Curiosity:** Makes readers want to learn more
- **Outcome:** Focuses on results
- **Contrarian:** Challenges common beliefs

### 3. Context Sources
When using Advanced mode:
- Expander at bottom shows sources used
- Lists files/docs analyzed for context

### 4. Brand DNA Learning
In Agentic Studio:
- Paste 3-10 past posts
- AI learns your writing style
- All 3 variants match your voice

### 5. Engagement Predictions
In Agentic Studio results:
- Shows predicted impressions
- Estimates likes/comments
- Calculates virality score

---

## 📚 Resources

### Documentation
- [UI_UX_UPGRADE_COMPLETE.md](UI_UX_UPGRADE_COMPLETE.md) — Full upgrade details
- [COLOR_THEME_REFERENCE.md](COLOR_THEME_REFERENCE.md) — Color palette guide
- [QUICK_START_NEW_UI.md](QUICK_START_NEW_UI.md) — Getting started
- [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) — What changed

### Code Files
- [ui/styles.py](ui/styles.py) — Theme system & CSS
- [ui/components.py](ui/components.py) — UI components
- [ui/agent_dashboard.py](ui/agent_dashboard.py) — Agent workflow UI
- [ui/multi_modal_input.py](ui/multi_modal_input.py) — Multi-input form
- [app.py](app.py) — Main application

---

## 🚀 Quick Command Reference

```bash
# Start the app
streamlit run app.py

# Clear cache and restart
streamlit run app.py --server.runOnSave true

# Open in browser (auto-opens by default)
# URL: http://localhost:8501
```

---

**🎊 You're now an expert in navigating the new premium UI!** 🚀
