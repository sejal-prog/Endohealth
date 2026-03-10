# 🌸 Endo Health Blog Header Generator

**AI Solutions Engineer Challenge - Built for Endo Health GmbH**

An AI-powered tool that generates consistent, brand-aligned header images for endometriosis blog posts using Google's Gemini 2.5 Flash Image API.

![Endo Health](https://img.shields.io/badge/Built%20for-Endo%20Health%20GmbH-8B2346)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **🎨 Brand-Consistent Images**: Generates abstract header images in Endo Health's burgundy/pink color palette
- **🧠 Smart Prompt Engineering**: Maps blog topics to visual concepts for consistent styling
- **💰 Zero Cost**: Uses Google Gemini free tier (500 images/day)
- **🔒 Usage Protection**: Session limits prevent API abuse
- **📱 Responsive UI**: Clean, professional interface matching Endo Health branding

---

## 🚀 Quick Deploy to Render

### 1. Fork/Clone this Repository

```bash
git clone https://github.com/YOUR_USERNAME/endo-header-generator.git
```

### 2. Get a Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (no credit card required!)

### 3. Deploy to Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` settings
5. Add Environment Variable:
   - Key: `GEMINI_API_KEY`
   - Value: *your API key from step 2*
6. Click **Deploy!**

Your app will be live at: `https://endo-header-generator.onrender.com`

---

## 🖥️ Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/endo-header-generator.git
cd endo-header-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Run the app
python main.py
```

Open http://localhost:5000 in your browser.

---

## 🎨 Brand Guidelines Implemented

Colors extracted from [endometriose.app](https://endometriose.app):

| Color | Hex | Usage |
|-------|-----|-------|
| Primary (Burgundy) | `#8B2346` | Headers, buttons, accents |
| Secondary (Soft Pink) | `#F8E8EC` | Backgrounds, cards |
| Accent (Rose) | `#D4A5B5` | Subtle highlights |
| Background | `#FDF8F9` | Page background |

### Visual Style
- Abstract, supportive imagery
- No human faces or text in images
- Warm, hopeful mood
- Organic flowing shapes
- Professional healthcare aesthetic

---

## 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────┐
│                  Flask App                       │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────────┐ │
│  │   Routes    │    │   Prompt Engineering    │ │
│  │  - /        │    │  - BASE_STYLE           │ │
│  │  - /generate│───▶│  - VISUAL_CONCEPTS      │ │
│  │  - /status  │    │  - Topic Mapping        │ │
│  └─────────────┘    └───────────┬─────────────┘ │
│                                 │               │
│                     ┌───────────▼─────────────┐ │
│                     │   Google Gemini API     │ │
│                     │  gemini-2.5-flash-image │ │
│                     │    (FREE: 500/day)      │ │
│                     └─────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI |
| `/generate` | POST | Generate single image |
| `/api/status` | GET | API health & usage stats |
| `/health` | GET | Health check for Render |

### Generate Image Request

```json
POST /generate
{
  "title": "5 Gentle Exercises for Pelvic Pain Relief",
  "session_id": "sess_12345"
}
```

### Response

```json
{
  "success": true,
  "title": "5 Gentle Exercises for Pelvic Pain Relief",
  "image": "base64_encoded_image_data..."
}
```

---

## 🛡️ Cost Protection

- **Session Limit**: 10 images per session
- **Daily Limit Display**: Shows Gemini's 500/day free tier
- **Usage Tracking**: Stored in `usage_data.json` (resets daily)
- **No API Key Exposure**: Key read from environment variable only

---

## 📁 Project Structure

```
endo-header-generator/
├── main.py              # Flask app + Gemini API integration
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── static/
    └── generated/      # Output directory for images
```

---

## 🤝 Built For

**Endo Health GmbH** - [endometriose.app](https://endometriose.app)

A DiGA-certified digital health application helping women manage endometriosis through symptom tracking, personalized insights, and evidence-based support.

---

## 📝 License

MIT License - Feel free to use and modify.

---

## 👩‍💻 Author

Built with 💛 for women's health

*AI Solutions Engineer Challenge Submission*
