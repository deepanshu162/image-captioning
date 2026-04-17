from flask import Flask, request, jsonify, render_template
import os
import subprocess
import json
import uuid

app = Flask(__name__)
# Ensure .tmp exists for uploaded files
os.makedirs(".tmp", exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        # Save file to .tmp with a unique name
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = '.png'
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(".tmp", filename)
        
        file.save(filepath)
        
        # Execute the standalone image_captioning script
        # Using subprocess to maintain the 3-Layer Architecture separation
        try:
            result = subprocess.run(
                ["python", "execution/image_captioning.py", filepath],
                capture_output=True,
                text=True,
                check=True
            )
            
            # The script prints JSON to standard output.
            # We must parse it. Sometimes there's debug output from transformers,
            # so we'll look for the last line that parses as JSON.
            lines = result.stdout.strip().split('\n')
            parsed_result = None
            for line in reversed(lines):
                if not line.strip(): continue
                try:
                    parsed_result = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
            
            if parsed_result is None:
                return jsonify({"error": "Failed to parse model output"}), 500
                
            return jsonify(parsed_result)
            
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Script execution failed: {e.stderr}"}), 500
        finally:
            # Clean up the temp file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
