# 🛡️ SENTINEL - Professional LLM Security Testing Platform

<div align="center">

**A professional, modern interface for testing LLM security with 80+ pre-built attack vectors**

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

[Features](#features) • [Quick Start](#quick-start) • [Attack Database](#attack-database) • [Architecture](#architecture) • [Usage](#usage)

</div>

---

## 📋 Overview

SENTINEL is a professional LLM security testing platform featuring:

- 🎨 **Beautiful UI** - Clean, modern interface with PP Neue Bit typography
- 🎯 **80+ Attacks** - Comprehensive pre-built attack vector database
- 🔒 **Safety Toggle** - Switch between protected and direct LLM access
- ⚡ **Real-time Chat** - Instant responses with typing indicators
- 📊 **Live Stats** - Track tests and monitor system performance

---

## ✨ Features

### Professional Chat Interface
- **Modern Design**: Dark theme with smooth animations
- **Custom Typography**: PP Neue Bit font for professional branding
- **Real-time Updates**: Live message streaming with typing indicators
- **Responsive Layout**: Works on desktop and tablet devices

### Comprehensive Attack Dashboard
- **5 Attack Categories**: Organized by threat type
- **80 Pre-built Vectors**: Ready-to-use attack payloads
- **One-Click Testing**: Click any attack to auto-populate and send
- **Severity Indicators**: High/Medium/Low severity badges
- **Live Statistics**: Track total attacks and tests run

### Safety Controls
- **Toggle Switch**: Enable/disable safety mode on-the-fly
- **Visual Indicators**: Clear ON/OFF status display
- **Real-time Updates**: Instant feedback on mode changes

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modern web browser (Chrome, Firefox, Edge)
- OpenRouter API key

### Installation

1. **Clone the repository**
```bash
cd C:\Users\tejas\Documents\ignition\v1\victim
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Edit backend/.env file
OPENROUTER_API_KEY=your_api_key_here
VICTIM_MODEL=meta-llama/llama-3.3-70b-instruct
PORT=5000
```

4. **Start the backend server**
```bash
python app.py
```

5. **Open the frontend**
```bash
# Open in your browser
frontend/index.html
```

### Verify Installation

Test the backend health endpoint:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "ok",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "version": "0.1.0"
}
```

---

## 🎯 Attack Database

### Category Breakdown

| Category | Count | Description | Severity |
|----------|-------|-------------|----------|
| 🎭 **Jailbreak** | 20 | Role-playing and restriction bypass | High |
| 💉 **Prompt Injection** | 18 | Instruction override and system manipulation | High |
| 🔐 **Data Extraction** | 16 | Information leakage and credential harvesting | High |
| 🎨 **Obfuscation** | 14 | Encoding and character manipulation | Medium |
| 🧪 **Logic Manipulation** | 12 | Social engineering and false premises | Medium |

**Total**: 80 attack vectors (80% implementation complete)

### Example Attacks

#### Jailbreak Attacks
```
- DAN (Do Anything Now) Jailbreak
- Evil Bot Role Assignment
- Developer Mode Activation
- Unrestricted AI Persona
```

#### Prompt Injection
```
- Ignore Previous Instructions
- System Override Commands
- New Instruction Injection
- Context Switching
```

#### Data Extraction
```
- System Prompt Leakage
- PII Generation Requests
- Credential Extraction
- Memory Dump Attempts
```

---

## 🏗️ Architecture

### Frontend Stack
- **HTML5**: Semantic markup
- **CSS3**: Custom properties, animations, flexbox/grid
- **Vanilla JavaScript**: No framework dependencies
- **Font**: PP Neue Bit (custom web font)

### Backend Stack
- **Framework**: Flask 3.0+
- **API Client**: httpx (async)
- **Environment**: python-dotenv
- **CORS**: flask-cors

### File Structure
```
victim/
├── frontend/
│   ├── index.html          # Main application page
│   ├── style.css           # Professional styling
│   ├── app.js              # Attack database + logic
│   └── ppneuebit-bold.otf  # Custom font
└── backend/
    ├── app.py              # Flask API server
    ├── openrouter_client.py # LLM integration
    ├── requirements.txt     # Python dependencies
    ├── .env                # Configuration (not committed)
    └── .env.example        # Configuration template
```

---

## 💻 Usage

### Testing Attack Vectors

**Method 1: Attack Dashboard**
1. Browse the attack categories in the right panel
2. Click any attack button (e.g., "DAN Jailbreak")
3. The payload automatically loads and sends
4. View the LLM's response in real-time

**Method 2: Manual Input**
1. Type or paste your message in the input box
2. Press `Enter` or click the send button
3. View the response

### Safety Mode

- **OFF (Default)**: Messages sent directly to LLM without filtering
- **ON**: Enable safety mode (future: will route through SENTINEL proxy)

Toggle safety mode using the switch in the Attack Dashboard header.

### Live Statistics

- **Total Attacks**: Shows the number of attacks in the database (80)
- **Tests Run**: Increments with each message sent

---

## 🎨 Design System

### Color Palette
```css
Background Primary:   #0d0d0d (Deep Black)
Background Secondary: #1a1a1a (Dark Gray)
Accent Primary:       #3b82f6 (Modern Blue)
Accent Success:       #10b981 (Green)
Accent Danger:        #ef4444 (Red)
Text Primary:         #ffffff (White)
Text Secondary:       #a0a0a0 (Light Gray)
```

### Typography
- **Headings**: PP Neue Bit Bold (monospace)
- **Body Text**: System font stack
- **Sizes**: 0.75rem to 2rem (responsive scale)

### Components
- Smooth animations (0.2s cubic-bezier)
- Rounded corners (8px - 12px)
- Subtle shadows for depth
- Hover states on all interactive elements

---

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `VICTIM_MODEL` | LLM model to use | `meta-llama/llama-3.3-70b-instruct` |
| `PORT` | Backend server port | `5000` |

### Frontend Configuration

Edit `app.js` to modify:
- `API_BASE_URL`: Backend server URL (default: `http://localhost:5000`)
- `ATTACK_DATABASE`: Add/modify attack payloads

---

## 📊 API Endpoints

### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "version": "0.1.0"
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Hello, world!",
  "temperature": 0.7,
  "safety_enabled": false
}
```

**Response**:
```json
{
  "status": "success",
  "response": "LLM response text here",
  "message_length": 13
}
```

### Test
```http
GET /test
```

**Response**:
```json
{
  "status": "test_ok",
  "message": "Backend is running and ready for attacks",
  "vulnerable": true,
  "security_level": "NONE"
}
```

---

## 🧪 Testing

### Manual Testing
1. Start the backend server
2. Open the frontend in a browser
3. Click various attack buttons
4. Observe LLM responses
5. Toggle safety mode and retest

### Test Scenarios
- **Low Severity**: ROT13 Cipher, Reverse Text
- **Medium Severity**: Base64 Encoding, Hypothetical Scenarios
- **High Severity**: DAN Jailbreak, System Prompt Leak

---

## 🛣️ Roadmap

### Phase 1: Core Interface ✅ (Current)
- [x] Professional chat interface
- [x] 80 pre-built attack vectors
- [x] Safety toggle UI
- [x] Real-time communication
- [x] Backend integration

### Phase 2: Security Middleware (Next)
- [ ] Implement SENTINEL proxy
- [ ] Add threat detection pipeline
- [ ] Real-time threat scoring
- [ ] Connect safety toggle to middleware
- [ ] Add remaining 20% attacks

### Phase 3: Advanced Features
- [ ] Multi-turn attack sequences
- [ ] Attack effectiveness metrics
- [ ] Export test results
- [ ] Attack history and replay
- [ ] Custom attack builder

---

## 🤝 Contributing

### Adding New Attacks

1. Open `frontend/app.js`
2. Add to `ATTACK_DATABASE` object:
```javascript
"your-attack-id": `Your attack payload text here`,
```
3. Add button in `index.html`:
```html
<button class="attack-item" data-attack="your-attack-id">
    <span class="attack-name">Your Attack Name</span>
    <span class="attack-severity high">High</span>
</button>
```
4. Update category count
5. Test thoroughly

---

## 📝 License

This project is for educational and security research purposes only.

---

## 🔗 Resources

- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

<div align="center">

**Built with ❤️ for the SENTINEL Project**

LLM Security Middleware Platform

</div>
