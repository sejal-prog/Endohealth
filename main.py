"""
Endo Health Blog Header Image Generator
AI Solutions Engineer Challenge - Built for Endo Health GmbH

Generates consistent, brand-aligned header images for endometriosis blog posts
using Google's Gemini 2.5 Flash Image (FREE tier - 500 images/day).

Author: Sejal
"""

import os
import json
import base64
from datetime import date
from flask import Flask, request, jsonify
from pathlib import Path

# Import Google Gen AI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'endo-health-secret-key')

# ============================================================================
# BRAND COLORS (extracted from endometriose.app)
# ============================================================================
BRAND = {
    'primary': '#8B2346',       # Deep burgundy/maroon
    'primary_light': '#A62D55',
    'primary_dark': '#6B1A36',
    'secondary': '#F8E8EC',     # Soft pink
    'accent': '#D4A5B5',        # Rose
    'background': '#FDF8F9',
    'text': '#4A4A4A'
}

MAX_PER_SESSION = 10
DAILY_LIMIT = 500

# ============================================================================
# PROMPT ENGINEERING FOR BRAND CONSISTENCY
# ============================================================================
BASE_STYLE = """Create a modern minimalist blog header image:
- Soft warm colors: burgundy (#8B2346), soft pink, rose, cream
- Clean vector or watercolor illustration style
- Abstract, supportive, empowering healthcare aesthetic
- Gentle gradients, organic flowing shapes
- NO human faces, NO text/words/letters, NO medical equipment
- Warm hopeful mood, professional healthcare blog aesthetic"""

VISUAL_CONCEPTS = {
    'cycle': 'circular flowing patterns, moon phases, gentle rhythmic waves',
    'menstrual': 'circular patterns, rhythmic waves in soft rose tones',
    'exercise': 'gentle movement lines, yoga-inspired curves, peaceful motion',
    'yoga': 'balanced organic shapes, zen minimalism, peaceful curves',
    'nutrition': 'organic leaf shapes, botanical abstracts, natural forms',
    'food': 'abstract organic shapes, gentle natural patterns',
    'stress': 'transitioning patterns from complex to calm, soothing gradients',
    'anxiety': 'gentle calming waves, soft reassuring patterns',
    'partner': 'intertwined abstract shapes, connected flowing forms',
    'support': 'embracing shapes, protective gentle curves',
    'tracking': 'gentle data-inspired patterns, soft rhythmic markers',
    'symptoms': 'abstract body awareness patterns, mindful abstracts',
    'doctor': 'professional caring abstracts, healthcare trust patterns',
    'appointment': 'prepared organized patterns, confident calm visuals',
    'self-care': 'nurturing cocoon shapes, peaceful sanctuary visuals',
    'community': 'connected abstract network, supportive group patterns',
    'pain': 'soothing wave patterns, gentle relief abstracts',
    'relief': 'releasing tension abstracts, peaceful resolution',
    'healing': 'gentle recovery patterns, nurturing growth abstracts',
    'pelvic': 'gentle core-centered abstracts, supportive foundation'
}

DEFAULT_CONCEPT = 'gentle abstract flowing shapes, burgundy and soft pink gradients, supportive feminine healthcare aesthetic, warm hopeful mood'

SAMPLE_TITLES = [
    "Understanding Your Menstrual Cycle with Endometriosis",
    "5 Gentle Exercises for Pelvic Pain Relief",
    "Nutrition Tips: Anti-Inflammatory Foods That Help"
]

# ============================================================================
# USAGE TRACKING (protects free tier)
# ============================================================================
USAGE_FILE = 'usage_data.json'

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'r') as f:
                data = json.load(f)
                if data.get('date') != str(date.today()):
                    return {'date': str(date.today()), 'count': 0, 'sessions': {}}
                return data
        except:
            pass
    return {'date': str(date.today()), 'count': 0, 'sessions': {}}

def save_usage(data):
    try:
        with open(USAGE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def get_session_count(session_id):
    return load_usage().get('sessions', {}).get(session_id, 0)

def increment_usage(session_id):
    usage = load_usage()
    usage['count'] = usage.get('count', 0) + 1
    usage.setdefault('sessions', {})[session_id] = usage['sessions'].get(session_id, 0) + 1
    save_usage(usage)

# ============================================================================
# IMAGE GENERATION
# ============================================================================
def get_visual_concept(title):
    """Map blog title keywords to visual concepts."""
    title_lower = title.lower()
    matched = [c for k, c in VISUAL_CONCEPTS.items() if k in title_lower]
    return ' Combined with '.join(matched[:2]) if matched else DEFAULT_CONCEPT

def create_prompt(title):
    """Create full image generation prompt with brand guidelines."""
    concept = get_visual_concept(title)
    return f"""{BASE_STYLE}

Visual concept: {concept}
Topic context (for mood only, DO NOT include any text in the image): "{title}"

Create a beautiful abstract header image that evokes this topic with burgundy and soft pink colors."""

def generate_image(title):
    """Generate image using Gemini 2.5 Flash Image API."""
    if not GENAI_AVAILABLE:
        return None, "google-genai package not installed. Run: pip install google-genai"
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None, "GEMINI_API_KEY environment variable not set"
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        prompt = create_prompt(title)
        
        # Generate image using Gemini 2.5 Flash Image (Nano Banana)
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        
        # Extract image from response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_bytes = part.inline_data.data
                    if isinstance(image_bytes, bytes):
                        return base64.b64encode(image_bytes).decode('utf-8'), None
                    elif isinstance(image_bytes, str):
                        return image_bytes, None
        
        return None, "No image generated. Model may not support image generation for this prompt."
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return None, "Model not available. Verify API key has image generation access."
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return None, "Rate limit reached. Please wait and try again."
        elif "permission" in error_msg.lower() or "403" in error_msg:
            return None, "API key lacks image generation permission. Get a new key at aistudio.google.com"
        else:
            return None, f"API Error: {error_msg}"

# ============================================================================
# FLASK ROUTES
# ============================================================================
@app.route('/')
def index():
    """Serve the main application page."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Header Generator | Endo Health</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, {BRAND['background']} 0%, {BRAND['secondary']} 100%);
            min-height: 100vh;
            color: {BRAND['text']};
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 24px; }}
        
        /* Header */
        .header {{ text-align: center; margin-bottom: 40px; }}
        .logo {{ display: inline-flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
        .logo-icon {{
            width: 48px; height: 48px;
            background: {BRAND['primary']};
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: bold; font-size: 20px;
        }}
        .logo-text {{ font-size: 24px; font-weight: 600; color: {BRAND['primary']}; }}
        .header h1 {{ font-size: 28px; font-weight: 700; color: {BRAND['primary_dark']}; margin-bottom: 8px; }}
        .header p {{ font-size: 15px; opacity: 0.7; }}
        
        /* Card */
        .card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 24px rgba(139, 35, 70, 0.08);
            padding: 28px;
            margin-bottom: 24px;
        }}
        .badge {{
            display: inline-flex; align-items: center; gap: 6px;
            padding: 6px 12px;
            background: {BRAND['secondary']};
            border-radius: 20px;
            font-size: 12px;
            color: {BRAND['primary']};
            margin-bottom: 20px;
        }}
        .dot {{ width: 8px; height: 8px; background: #22C55E; border-radius: 50%; }}
        .label {{ 
            font-size: 13px; font-weight: 600; 
            color: {BRAND['primary']}; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            margin-bottom: 12px; 
        }}
        
        /* Form */
        textarea {{
            width: 100%; padding: 14px;
            border: 2px solid {BRAND['secondary']};
            border-radius: 12px;
            font-family: inherit; font-size: 14px;
            resize: vertical; min-height: 100px;
            color: {BRAND['text']};
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        textarea:focus {{ 
            outline: none; 
            border-color: {BRAND['primary']}; 
            box-shadow: 0 0 0 3px rgba(139, 35, 70, 0.1);
        }}
        .hint {{ font-size: 12px; opacity: 0.6; margin: 8px 0 20px; }}
        
        /* Button */
        .btn {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 12px 24px;
            background: linear-gradient(135deg, {BRAND['primary']} 0%, {BRAND['primary_light']} 100%);
            color: white; border: none; border-radius: 10px;
            font-size: 14px; font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(139, 35, 70, 0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(139, 35, 70, 0.4); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        
        /* Results */
        .results {{ display: none; }}
        .results.active {{ display: block; }}
        .result {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(139, 35, 70, 0.08);
            margin-bottom: 20px;
            animation: fadeIn 0.4s ease;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; }} }}
        .result img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; background: {BRAND['secondary']}; }}
        .result-info {{ padding: 14px 18px; border-top: 1px solid {BRAND['secondary']}; }}
        .result-title {{ font-size: 13px; font-weight: 500; margin-bottom: 8px; }}
        .btn-sm {{
            padding: 6px 14px; font-size: 12px;
            border-radius: 6px;
            background: {BRAND['secondary']};
            color: {BRAND['primary']};
            border: none; font-weight: 500; cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }}
        .btn-sm:hover {{ background: {BRAND['primary']}; color: white; }}
        
        /* Error */
        .error {{ 
            background: #FEF2F2; 
            border: 1px solid #FECACA; 
            border-radius: 10px; 
            padding: 12px; 
            color: #991B1B; 
            font-size: 13px; 
        }}
        
        /* Loading */
        .loading {{ display: none; text-align: center; padding: 40px; }}
        .loading.active {{ display: block; }}
        .spinner {{
            width: 40px; height: 40px;
            border: 3px solid {BRAND['secondary']};
            border-top-color: {BRAND['primary']};
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 12px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .loading-text {{ color: {BRAND['primary']}; font-weight: 500; font-size: 14px; }}
        
        /* Progress */
        .progress {{ height: 4px; background: {BRAND['secondary']}; border-radius: 2px; margin-bottom: 16px; display: none; }}
        .progress.active {{ display: block; }}
        .progress-bar {{ height: 100%; background: {BRAND['primary']}; width: 0%; transition: width 0.3s; }}
        
        /* Footer */
        .footer {{ text-align: center; padding: 30px 0; opacity: 0.5; font-size: 12px; }}
        .footer a {{ color: {BRAND['primary']}; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">E</div>
                <span class="logo-text">Endo Health</span>
            </div>
            <h1>Blog Header Generator</h1>
            <p>Create beautiful, brand-consistent header images with AI</p>
        </div>
        
        <div class="card">
            <div class="badge"><span class="dot"></span> Gemini AI • Free Tier (500/day)</div>
            <div class="label">📝 Blog Titles</div>
            <textarea id="titles" placeholder="Enter blog titles, one per line...">{chr(10).join(SAMPLE_TITLES)}</textarea>
            <p class="hint">One title per line. Each generates a unique, brand-consistent header image.</p>
            <button class="btn" onclick="generate()" id="btn">▶ Generate Headers</button>
        </div>
        
        <div class="progress" id="progress"><div class="progress-bar" id="bar"></div></div>
        <div class="loading" id="loading"><div class="spinner"></div><p class="loading-text" id="status">Generating...</p></div>
        <div class="results" id="results"></div>
        
        <div class="footer">
            Built for <a href="https://endometriose.app" target="_blank">Endo Health GmbH</a> • AI Solutions Engineer Challenge<br>
            Made with 💛 for women's health
        </div>
    </div>
    
    <script>
        const sid = 'sess_' + Date.now();
        let count = 0;
        
        async function generate() {{
            const text = document.getElementById('titles').value.trim();
            if (!text) {{ alert('Enter at least one title'); return; }}
            
            const titles = text.split('\\n').filter(t => t.trim());
            if (!titles.length) {{ alert('Enter at least one title'); return; }}
            
            if (count + titles.length > {MAX_PER_SESSION}) {{
                alert('Session limit: ' + ({MAX_PER_SESSION} - count) + ' images remaining');
                return;
            }}
            
            document.getElementById('btn').disabled = true;
            document.getElementById('loading').classList.add('active');
            document.getElementById('progress').classList.add('active');
            document.getElementById('results').innerHTML = '';
            document.getElementById('results').classList.remove('active');
            
            const bar = document.getElementById('bar');
            const status = document.getElementById('status');
            const results = [];
            
            for (let i = 0; i < titles.length; i++) {{
                status.textContent = 'Generating: ' + titles[i].substring(0, 30) + '...';
                try {{
                    const res = await fetch('/generate', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{title: titles[i].trim(), session_id: sid}})
                    }});
                    const data = await res.json();
                    results.push({{title: titles[i].trim(), ...data}});
                    if (data.success) count++;
                }} catch (e) {{
                    results.push({{title: titles[i].trim(), success: false, error: 'Network error'}});
                }}
                bar.style.width = ((i + 1) / titles.length * 100) + '%';
            }}
            
            document.getElementById('btn').disabled = false;
            document.getElementById('loading').classList.remove('active');
            document.getElementById('progress').classList.remove('active');
            bar.style.width = '0%';
            showResults(results);
        }}
        
        function showResults(results) {{
            const container = document.getElementById('results');
            container.classList.add('active');
            
            results.forEach((r, i) => {{
                const div = document.createElement('div');
                div.className = 'result';
                if (r.success && r.image) {{
                    div.innerHTML = `
                        <img src="data:image/png;base64,${{r.image}}" alt="${{r.title}}">
                        <div class="result-info">
                            <div class="result-title">${{r.title}}</div>
                            <button class="btn-sm" onclick="download('${{r.image}}','header_${{i+1}}.png')">Download PNG</button>
                        </div>`;
                }} else {{
                    div.innerHTML = `
                        <div style="padding:30px;text-align:center;background:{BRAND['secondary']}">
                            <div style="font-size:36px;margin-bottom:8px">⚠️</div>
                            <p style="color:{BRAND['primary']};font-weight:500">Generation Failed</p>
                        </div>
                        <div class="result-info">
                            <div class="result-title">${{r.title}}</div>
                            <div class="error">${{r.error || 'Unknown error'}}</div>
                        </div>`;
                }}
                container.appendChild(div);
            }});
        }}
        
        function download(data, name) {{
            const a = document.createElement('a');
            a.href = 'data:image/png;base64,' + data;
            a.download = name;
            a.click();
        }}
    </script>
</body>
</html>'''

@app.route('/generate', methods=['POST'])
def gen():
    """Generate a single header image."""
    data = request.get_json()
    title = data.get('title', '').strip()
    session_id = data.get('session_id', 'unknown')
    
    if not title:
        return jsonify({'success': False, 'error': 'No title provided'})
    
    if get_session_count(session_id) >= MAX_PER_SESSION:
        return jsonify({'success': False, 'error': f'Session limit reached ({MAX_PER_SESSION} images)'})
    
    image, error = generate_image(title)
    
    if image:
        increment_usage(session_id)
        return jsonify({'success': True, 'image': image, 'title': title})
    return jsonify({'success': False, 'error': error or 'Failed to generate image'})

@app.route('/api/status')
def status():
    """API status endpoint for health checks."""
    usage = load_usage()
    return jsonify({
        'status': 'operational',
        'gemini_key_set': bool(os.environ.get('GEMINI_API_KEY')),
        'genai_sdk_available': GENAI_AVAILABLE,
        'daily_usage': usage.get('count', 0),
        'daily_limit': DAILY_LIMIT,
        'session_limit': MAX_PER_SESSION
    })

@app.route('/health')
def health():
    """Health check for Render."""
    return 'OK', 200

# Create static directory
Path('static/generated').mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
