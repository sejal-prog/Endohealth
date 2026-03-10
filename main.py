"""
Endo Health Blog Header Image Generator
AI Solutions Engineer Challenge - Built for Endo Health GmbH
"""

import os
import json
import base64
from datetime import date
from flask import Flask, request, jsonify
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'endo-health-secret-key')

# Brand Colors
BRAND = {
    'primary': '#8B2346',
    'primary_light': '#A62D55',
    'primary_dark': '#6B1A36',
    'secondary': '#F8E8EC',
    'background': '#FDF8F9',
    'text': '#4A4A4A'
}

MAX_PER_SESSION = 10
USAGE_FILE = 'usage_data.json'

# Prompts
BASE_STYLE = """Create a modern minimalist blog header image:
- Colors: burgundy (#8B2346), soft pink, rose, cream
- Style: clean vector or watercolor illustration
- Abstract, supportive healthcare aesthetic
- NO faces, NO text/words, NO medical equipment
- Warm hopeful mood"""

CONCEPTS = {
    'cycle': 'circular flowing patterns, moon phases, gentle waves',
    'menstrual': 'circular patterns, rhythmic waves in rose tones',
    'exercise': 'gentle movement lines, yoga curves',
    'nutrition': 'organic leaf shapes, botanical abstracts',
    'stress': 'transitioning patterns, soothing gradients',
    'partner': 'intertwined abstract shapes, connected forms',
    'support': 'embracing shapes, protective curves',
    'doctor': 'professional caring abstracts',
    'self-care': 'nurturing cocoon shapes, peaceful sanctuary',
    'community': 'connected network patterns',
    'pain': 'soothing wave patterns, gentle relief',
    'healing': 'gentle recovery patterns, growth abstracts'
}

SAMPLE_TITLES = [
    "Understanding Your Menstrual Cycle with Endometriosis",
    "5 Gentle Exercises for Pelvic Pain Relief",
    "Nutrition Tips: Anti-Inflammatory Foods That Help"
]

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

def get_concept(title):
    title_lower = title.lower()
    matched = [c for k, c in CONCEPTS.items() if k in title_lower]
    return ' and '.join(matched[:2]) if matched else 'gentle abstract flowing shapes with burgundy and pink gradients'

def create_prompt(title):
    concept = get_concept(title)
    return f"{BASE_STYLE}\n\nVisual concept: {concept}\nTopic (mood only, no text): {title}"

def generate_image(title):
    """Generate image using Gemini 2.5 Flash Image (Nano Banana)."""
    if not GENAI_AVAILABLE:
        return None, "google-genai package not installed"
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None, "GEMINI_API_KEY not set"
    
    try:
        client = genai.Client(api_key=api_key)
        prompt = create_prompt(title)
        
        # Use gemini-2.5-flash-image (confirmed working, production model)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                )
            ),
        )
        
        # Extract image
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    data = part.inline_data.data
                    if isinstance(data, bytes):
                        return base64.b64encode(data).decode('utf-8'), None
                    return data, None
        
        return None, "No image in response"
        
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/')
def index():
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
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, {BRAND['background']} 0%, {BRAND['secondary']} 100%);
            min-height: 100vh;
            color: {BRAND['text']};
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 24px; }}
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
        .label {{ font-size: 13px; font-weight: 600; color: {BRAND['primary']}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
        textarea {{
            width: 100%; padding: 14px;
            border: 2px solid {BRAND['secondary']};
            border-radius: 12px;
            font-family: inherit; font-size: 14px;
            resize: vertical; min-height: 100px;
            color: {BRAND['text']};
        }}
        textarea:focus {{ outline: none; border-color: {BRAND['primary']}; }}
        .hint {{ font-size: 12px; opacity: 0.6; margin: 8px 0 20px; }}
        .btn {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 12px 24px;
            background: linear-gradient(135deg, {BRAND['primary']} 0%, {BRAND['primary_light']} 100%);
            color: white; border: none; border-radius: 10px;
            font-size: 14px; font-weight: 600; cursor: pointer;
            box-shadow: 0 4px 12px rgba(139, 35, 70, 0.3);
        }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        .results {{ display: none; }}
        .results.active {{ display: block; }}
        .result {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(139, 35, 70, 0.08);
            margin-bottom: 20px;
        }}
        .result img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; background: {BRAND['secondary']}; }}
        .result-info {{ padding: 14px 18px; border-top: 1px solid {BRAND['secondary']}; }}
        .result-title {{ font-size: 13px; font-weight: 500; margin-bottom: 8px; }}
        .btn-sm {{
            padding: 6px 14px; font-size: 12px; border-radius: 6px;
            background: {BRAND['secondary']}; color: {BRAND['primary']};
            border: none; font-weight: 500; cursor: pointer;
        }}
        .btn-sm:hover {{ background: {BRAND['primary']}; color: white; }}
        .error {{ background: #FEF2F2; border: 1px solid #FECACA; border-radius: 10px; padding: 12px; color: #991B1B; font-size: 13px; }}
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
        .loading-text {{ color: {BRAND['primary']}; font-weight: 500; }}
        .progress {{ height: 4px; background: {BRAND['secondary']}; border-radius: 2px; margin-bottom: 16px; display: none; }}
        .progress.active {{ display: block; }}
        .progress-bar {{ height: 100%; background: {BRAND['primary']}; width: 0%; transition: width 0.3s; }}
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
            <div class="badge"><span class="dot"></span> Gemini AI • Free Tier</div>
            <div class="label">📝 Blog Titles</div>
            <textarea id="titles">{chr(10).join(SAMPLE_TITLES)}</textarea>
            <p class="hint">One title per line. Each generates a unique header image.</p>
            <button class="btn" onclick="generate()" id="btn">▶ Generate Headers</button>
        </div>
        
        <div class="progress" id="progress"><div class="progress-bar" id="bar"></div></div>
        <div class="loading" id="loading"><div class="spinner"></div><p class="loading-text" id="status">Generating...</p></div>
        <div class="results" id="results"></div>
        
        <div class="footer">Built for <a href="https://endometriose.app">Endo Health GmbH</a> • AI Solutions Engineer Challenge</div>
    </div>
    
    <script>
        const sid = 'sess_' + Date.now();
        let count = 0;
        
        async function generate() {{
            const text = document.getElementById('titles').value.trim();
            if (!text) return alert('Enter at least one title');
            
            const titles = text.split('\\n').filter(t => t.trim());
            if (!titles.length) return alert('Enter at least one title');
            
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
    data = request.get_json()
    title = data.get('title', '').strip()
    session_id = data.get('session_id', 'unknown')
    
    if not title:
        return jsonify({'success': False, 'error': 'No title'})
    
    if get_session_count(session_id) >= MAX_PER_SESSION:
        return jsonify({'success': False, 'error': 'Session limit reached'})
    
    image, error = generate_image(title)
    
    if image:
        increment_usage(session_id)
        return jsonify({'success': True, 'image': image, 'title': title})
    return jsonify({'success': False, 'error': error})

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok',
        'genai': GENAI_AVAILABLE,
        'api_key': bool(os.environ.get('GEMINI_API_KEY'))
    })

Path('static/generated').mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
