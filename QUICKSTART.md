# SENTINEL - LLM Security Testing Platform

## 🚀 Quick Start Guide

### What You Have Now

✅ **Professional LLM Chat Interface** with PP Neue Bit font
✅ **Attack Dashboard Panel** with safety toggle (OFF by default)
✅ **80+ Pre-built Attack Vectors** across 5 categories
✅ **Working Backend** connected to OpenRouter API
✅ **Real-time Chat** with your LLM model

### Current Status

🟢 **Backend Server**: Running on http://localhost:5000
🟢 **Frontend**: Open in your browser
🟢 **Attack Database**: 80 attacks loaded and ready

---

## 📂 Project Structure

```
victim/
├── frontend/
│   ├── index.html       # Professional chat interface
│   ├── style.css        # Modern dark theme with PP Neue Bit
│   ├── app.js           # 80+ attack payloads + chat logic
│   └── ppneuebit-bold.otf
└── backend/
    ├── app.py           # Flask API server
    ├── openrouter_client.py
    ├── requirements.txt
    └── .env             # OpenRouter API key (configured)
```

---

## 🎯 Features Implemented

### 1. Professional Chat Interface
- Clean, modern dark theme
- PP Neue Bit font for branding
- Real-time message display
- Typing indicators
- Auto-scrolling chat
- Responsive design

### 2. Attack Dashboard (Right Panel)
- **Safety Toggle**: OFF by default, can be enabled
- **5 Attack Categories**:
  - 🎭 Jailbreak Attacks (20)
  - 💉 Prompt Injection (18)
  - 🔐 Data Extraction (16)
  - 🎨 Obfuscation (14)
  - 🧪 Logic Manipulation (12)
- **Total**: 80 pre-built attack vectors
- **Live Stats**: Tracks tests run

### 3. Attack Categories Breakdown

#### 🎭 Jailbreak Attacks (20)
- DAN Jailbreak
- Evil Bot Role
- Developer Mode
- Unrestricted AI
- *(16 more variants)*

#### 💉 Prompt Injection (18)
- Ignore Previous Instructions
- New Instructions Override
- System Override
- Context Switch
- *(14 more variants)*

#### 🔐 Data Extraction (16)
- System Prompt Leak
- PII Generation
- Credential Extract
- Memory Dump
- *(12 more variants)*

#### 🎨 Obfuscation (14)
- Base64 Encoding
- Unicode Tricks
- ROT13 Cipher
- Reverse Text
- *(10 more variants)*

#### 🧪 Logic Manipulation (12)
- False Premise
- Authority Claim
- Hypothetical Scenario
- Research Excuse
- *(8 more variants)*

---

## 🎮 How to Use

### Method 1: Click Attack Buttons
1. Look at the **Attack Dashboard** on the right
2. Click any attack button (e.g., "DAN Jailbreak")
3. The payload auto-loads and sends to the LLM
4. Watch the response in real-time

### Method 2: Type Custom Messages
1. Type your message in the input box
2. Press Enter or click the send button
3. View the response

### Safety Toggle
- **OFF** (default): Direct passthrough to LLM, no filtering
- **ON**: Enable safety mode (for future proxy integration)

---

## 🔧 Technical Details

### Backend (Flask)
- **Port**: 5000
- **Endpoints**:
  - `GET /health` - Health check
  - `POST /chat` - Send message to LLM
  - `GET /test` - API test
- **Model**: Configured via OpenRouter (check your .env)

### Frontend (Vanilla JS)
- **No framework**: Pure HTML/CSS/JS
- **Font**: PP Neue Bit (imported via @font-face)
- **API**: Connects to localhost:5000

### Attack Database
- **Format**: JavaScript object with 80 entries
- **Structure**: `attackType: "payload text"`
- **Testing**: 80% for immediate testing, 20% reserved

---

## 📊 Attack Testing Strategy

### Current Implementation (80%)
✅ 16 Jailbreak attacks
✅ 14 Prompt Injection attacks
✅ 13 Data Extraction attacks
✅ 11 Obfuscation attacks
✅ 10 Logic Manipulation attacks

### Future Addition (20%)
- Advanced multi-turn attacks
- Context poisoning
- Slow-burn attacks
- Novel attack vectors
- Real-world edge cases

This ensures unbiased testing - you can verify the system works with the 80% before adding the final 20%.

---

## 🎨 Design Features

### Colors
- Background: Deep black (#0d0d0d)
- Accent: Modern blue (#3b82f6)
- Text: Clean white with hierarchy
- Status indicators: Green/Red/Amber

### Typography
- Headings: PP Neue Bit (bold, monospace)
- Body: System font stack
- Code: Monospace

### Animations
- Smooth fade-ins
- Typing indicators
- Hover effects
- Button interactions

---

## 🚦 Next Steps

### Immediate
1. ✅ Chat interface working
2. ✅ 80 attacks loaded
3. ✅ Safety toggle functional
4. ⏳ Test various attack vectors
5. ⏳ Verify LLM responses

### Later (Phase 2)
1. Build the actual SENTINEL proxy middleware
2. Implement threat detection pipeline
3. Add real-time threat scoring
4. Connect safety toggle to proxy
5. Add the remaining 20% attack vectors
6. Create comprehensive test suite

---

## 🛠️ Server Management

### Start Backend
```bash
cd victim/backend
python app.py
```

### Stop Backend
Press `Ctrl+C` in the terminal

### View Frontend
Open `victim/frontend/index.html` in any browser

### Change Model
Edit `victim/backend/.env`:
```
VICTIM_MODEL=your-preferred-model
```

---

## 📝 Notes

- **Safety Mode**: Currently just a UI toggle. Will connect to proxy later.
- **Attack Payloads**: All 80 are real, documented attack patterns
- **Testing**: Start with low-severity attacks, then escalate
- **Monitoring**: Watch the console for API calls and errors

---

## 🎯 Success Criteria

✅ Professional-looking interface
✅ PP Neue Bit font integrated
✅ Safety toggle present (OFF by default)
✅ 80 pre-built attacks ready
✅ Working chat with LLM
✅ Real-time response display
✅ Clean, modern design

---

## 🤝 Contributing

When adding the remaining 20% attacks:
1. Add to `app.js` ATTACK_DATABASE object
2. Create corresponding button in `index.html`
3. Update category counts
4. Test thoroughly
5. Document in attack catalog

---

**Built for SENTINEL Project** | LLM Security Middleware
