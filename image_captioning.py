import os
import site

# Patch for Windows PyTorch DLL loading issue on Python 3.13+
if os.name == 'nt':
    try:
        for sp in site.getsitepackages():
            torch_lib = os.path.join(sp, 'torch', 'lib')
            if os.path.exists(torch_lib):
                os.add_dll_directory(torch_lib)
                break
    except Exception:
        pass

import argparse
import json
import sys
import requests
from io import BytesIO
from PIL import Image

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Ensure transformers and torch are installed."}))
    sys.exit(1)

def load_image(image_path_or_url):
    try:
        if image_path_or_url.startswith('http://') or image_path_or_url.startswith('https://'):
            response = requests.get(image_path_or_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert('RGB')
        else:
            return Image.open(image_path_or_url).convert('RGB')
    except Exception as e:
        print(json.dumps({"error": f"Failed to load image: {str(e)}"}))
        sys.exit(1)

def generate_caption(image_path):
    # Specify the pre-trained model
    model_id = "Salesforce/blip-image-captioning-base"
    
    try:
        # Load the processor and model
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)
        
        # Load the raw image
        raw_image = load_image(image_path)
        
        # Process and predict
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        # Return as JSON
        print(json.dumps({"caption": caption}))
        
    except Exception as e:
        print(json.dumps({"error": f"Failed to generate caption: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a caption for an input image.")
    parser.add_argument("image_path", type=str, help="The URL or local file path to the image.")
    args = parser.parse_args()
    
    generate_caption(args.image_path)
