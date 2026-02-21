# 🎨 COLOR THEME REFERENCE

## Light Mode 🌞

### Primary Colors
```css
Background:       #FFFFFF (White)
Background 2:     #F5F7FA (Light Gray)
Surface:          #FFFFFF (White)
Border:           #E2E8F0 (Light Border)
Text:             #111827 (Almost Black)
Text Muted:       #6B7280 (Gray)
```

### Accent Colors
```css
Primary:          #1D4ED8 (Bold Blue) 🔵
Accent Red:       #DC2626 (Bold Red) 🔴
Accent Black:     #111827 (Black) ⚫
Accent Cyan:      #06B6D4 (Cyan) 🔷
Success:          #16A34A (Green) ✅
Warning:          #D97706 (Orange) ⚠️
Error:            #DC2626 (Red) ❌
```

### Button Combos (Light Mode)
```
Button 1:  Red bg (#DC2626) + White text (#FFFFFF)     🔴⚪
Button 2:  Black bg (#111827) + White text (#FFFFFF)   ⚫⚪
Button 3:  Blue bg (#1D4ED8) + Cyan text (#06B6D4)     🔵🔷
Button 4:  White bg (#FFFFFF) + Red text (#DC2626)     ⚪🔴
```

### Gradient (Light Mode)
```css
Gradient Start:   #1D4ED8 (Blue)
Gradient Mid:     #DC2626 (Red)
Gradient End:     #111827 (Black)
```
**Result:** Blue → Red → Black (Bold & Professional)

---

## Dark Mode 🌙

### Primary Colors
```css
Background:       #0F172A (Dark Navy)
Background 2:     #1E293B (Lighter Navy)
Surface:          #1E293B (Lighter Navy)
Border:           #334155 (Border)
Text:             #F1F5F9 (Classic White)
Text Muted:       #94A3B8 (Light Gray)
```

### Accent Colors
```css
Primary:          #FACC15 (Bold Yellow) 🟡
Accent Red:       #F87171 (Light Red) 🔴
Accent Black:     #F1F5F9 (Classic White) ⚪
Accent Cyan:      #22D3EE (Bright Cyan) 🔷
Success:          #4ADE80 (Light Green) ✅
Warning:          #FACC15 (Yellow) ⚠️
Error:            #F87171 (Light Red) ❌
```

### Button Combos (Dark Mode)
```
Button 1:  Yellow bg (#FACC15) + Black text (#0F172A)       🟡⚫
Button 2:  Cyan bg (#22D3EE) + Black text (#0F172A)         🔷⚫
Button 3:  Green bg (#4ADE80) + Black text (#0F172A)        🟢⚫
Button 4:  White bg (#F1F5F9) + Red text (#DC2626)          ⚪🔴
```

### Gradient (Dark Mode)
```css
Gradient Start:   #FACC15 (Yellow)
Gradient Mid:     #22D3EE (Cyan)
Gradient End:     #4ADE80 (Light Green)
```
**Result:** Yellow → Cyan → Green (Vibrant & Modern)

---

## Mode-Specific Accent Borders

Used in post presentation cards (Agentic Studio variants):

### Storyteller
```css
Light Mode:  #1D4ED8 (Blue)   🔵
Dark Mode:   #FACC15 (Yellow) 🟡
```

### Strategist
```css
Light Mode:  #06B6D4 (Cyan)   🔷
Dark Mode:   #22D3EE (Cyan)   🔷
```

### Provocateur
```css
Light Mode:  #DC2626 (Red)    🔴
Dark Mode:   #F87171 (Red)    🔴
```

---

## Typography

### Font Families
```css
Headings/Titles/Buttons:  'Plus Jakarta Sans', sans-serif
Subtitles/Text/Labels:    'Poppins', sans-serif
Code Blocks:              'Poppins', sans-serif
```

### Font Weights
```css
Jakarta Sans:
  - 700 (Bold) — Headings, Button labels
  - 800 (ExtraBold) — Gradient titles

Poppins:
  - 300 (Light) — Subtle text
  - 400 (Regular) — Body text
  - 500 (Medium) — Labels
  - 600 (SemiBold) — Important text
```

### Font Sizes
```css
Gradient Title Large:    2.8rem (42px)   — Main app header
Gradient Title Medium:   1.6rem (25.6px) — Section headers
Gradient Title Small:    1.15rem (18.4px) — Sub-sections

Button Regular:          1.3rem (20.8px)
Button Primary:          1.5rem (24px)

Body Text:               1rem (16px)
Small Text:              0.85-0.9rem (13.6-14.4px)
```

---

## Border Radius
```css
Buttons:      14px (rounded-lg)
Cards:        16px (rounded-xl)
Inputs:       12px (rounded-md)
Expanders:    12px (rounded-md)
Metrics:      14px (rounded-lg)
```

---

## Shadows & Effects

### Cards
```css
Default:  0 4px 12px rgba(0,0,0,0.06)
Hover:    0 8px 24px rgba(0,0,0,0.1)
```

### Buttons
```css
Hover:    0 8px 24px rgba(0,0,0,0.15)
Primary:  0 10px 30px rgba(0,0,0,0.2)
```

### Loading Overlay
```css
Backdrop: backdrop-filter: blur(8px)
```

---

## Usage Examples

### Gradient Title
```html
<h1 class="gradient-title gradient-title-lg">
    LinkedIn Post Generator
</h1>
```
→ Creates shiny rainbow text with 3-color gradient

### Premium Card
```html
<div class="premium-card">
    <h3 class="gradient-title gradient-title-md">Section Title</h3>
    <p>Your content here</p>
</div>
```
→ Creates bordered card with hover effect

### Mode Card (Active State)
```html
<div class="mode-card active">
    <div class="mode-card-title">Simple Mode</div>
    <div class="mode-card-desc">Fast generation</div>
</div>
```
→ Creates card with gradient background when active

---

## CSS Variables

All colors are defined as CSS variables for easy theming:

```css
:root {
    --bg:             #FFFFFF / #0F172A
    --bg2:            #F5F7FA / #1E293B
    --surface:        #FFFFFF / #1E293B
    --border:         #E2E8F0 / #334155
    --text:           #111827 / #F1F5F9
    --text-muted:     #6B7280 / #94A3B8
    --primary:        #1D4ED8 / #FACC15
    --primary-hover:  #1E40AF / #EAB308
    --accent-red:     #DC2626 / #F87171
    --accent-cyan:    #06B6D4 / #22D3EE
    --success:        #16A34A / #4ADE80
    --warning:        #D97706 / #FACC15
    --error:          #DC2626 / #F87171
    --grad-start:     #1D4ED8 / #FACC15
    --grad-mid:       #DC2626 / #22D3EE
    --grad-end:       #111827 / #4ADE80
}
```

Use in CSS:
```css
.my-element {
    background: var(--surface);
    color: var(--text);
    border: 2px solid var(--border);
}
```

---

## Quick Reference Table

| Element              | Light Mode                  | Dark Mode                   |
|----------------------|-----------------------------|-----------------------------|
| Primary Color        | Blue (#1D4ED8)              | Yellow (#FACC15)            |
| Accent 1             | Red (#DC2626)               | Cyan (#22D3EE)              |
| Accent 2             | Black (#111827)             | White (#F1F5F9)             |
| Accent 3             | Cyan (#06B6D4)              | Green (#4ADE80)             |
| Gradient             | Blue→Red→Black              | Yellow→Cyan→Green           |
| Main Font            | Plus Jakarta Sans           | Plus Jakarta Sans           |
| Body Font            | Poppins                     | Poppins                     |
| Button Style         | 14px radius, 1.3-1.5rem     | 14px radius, 1.3-1.5rem     |
| Card Radius          | 16px                        | 16px                        |

---

## 🎨 Visual Preview

### Light Mode Look
```
┌────────────────────────────────────────┐
│  💼 LinkedIn Post Generator           │  ← Gradient title (Blue→Red→Black)
│  Transform ideas into posts with AI    │  ← Gray subtitle
├────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  │
│  │ ⚡ Simple     │  │ 🚀 Advanced   │  │  ← Mode cards (Blue border active)
│  │ Fast 1-3s    │  │ Enhanced 8s   │  │
│  └──────────────┘  └──────────────┘  │
├────────────────────────────────────────┤
│  [  📋 Copy Full Post  ]              │  ← Red bg + White text
│  [  📄 Copy Post Only  ]              │  ← Black bg + White text
│  [  #️⃣ Copy Hashtags ]              │  ← Blue bg + Cyan text
└────────────────────────────────────────┘
```

### Dark Mode Look
```
┌────────────────────────────────────────┐
│  💼 LinkedIn Post Generator           │  ← Gradient title (Yellow→Cyan→Green)
│  Transform ideas into posts with AI    │  ← Light gray subtitle
├────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  │
│  │ ⚡ Simple     │  │ 🚀 Advanced   │  │  ← Mode cards (Yellow border active)
│  │ Fast 1-3s    │  │ Enhanced 8s   │  │
│  └──────────────┘  └──────────────┘  │
├────────────────────────────────────────┤
│  [  📋 Copy Full Post  ]              │  ← Yellow bg + Black text
│  [  📄 Copy Post Only  ]              │  ← Cyan bg + Black text
│  [  #️⃣ Copy Hashtags ]              │  ← Green bg + Black text
└────────────────────────────────────────┘
```

---

**🎊 The entire UI now uses this bold, beautiful color system with perfect light/dark mode integration!**
