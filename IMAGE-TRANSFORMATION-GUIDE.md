# Image Transformation Service Setup Guide

## Overview
This guide explains how to set up and run the AI-powered interior design image transformation service for the Mukh Interiors website.

## Architecture

### Components
1. **Frontend** (HTML/CSS/JavaScript)
   - "Let's Know You Better" form to collect client preferences
   - Image upload functionality
   - Display of AI-generated room transformations

2. **Backend API** (Flask)
   - Handles image processing requests
   - Manages model loading and inference
   - Stores prompt history and generated images

3. **Image Transformation Service** (Python)
   - Depth extraction using ControlNet
   - AI image generation using Stable Diffusion
   - Detailed prompt building from client preferences

## Prerequisites

### System Requirements
- NVIDIA GPU (recommended: RTX 3060 or higher with 12GB+ VRAM)
- Python 3.8 or higher
- 50GB+ disk space for model downloads
- 16GB+ RAM

### Software
- Git
- Python pip
- Virtual environment (recommended)

## Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd interior-design-site
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask for API server
- PyTorch and TorchVision for deep learning
- Diffusers for Stable Diffusion pipelines
- Transformers for depth estimation models
- ControlNet utilities for depth-guided generation

### 4. Download Models (First Run)
Models will be automatically downloaded on first use. This requires:
- ~7GB for Stable Diffusion v1.5
- ~1GB for ControlNet Depth model
- ~500MB for DPT depth estimation

Models are cached in:
```
~/.cache/huggingface/hub/
```

## Running the Service

### 1. Start Flask API Server
```bash
python app.py
```

The server will start at `http://localhost:5000`

Expected output:
```
Starting Interior Design Image Transformation API Server
Upload folder: uploads
Max file size: 50.0MB
 * Running on http://0.0.0.0:5000
```

### 2. Update API URL in Frontend
In [script.js](script.js), update the API_BASE_URL:

```javascript
const API_BASE_URL = 'http://localhost:5000'; // Update for production
```

For production deployment, use your deployed API URL.

### 3. Open Frontend
Open [index.html](index.html) in a web browser or serve it via a web server:

```bash
# Using Python's built-in server (separate terminal)
python -m http.server 8000
# Then visit http://localhost:8000
```

## API Endpoints

### Health Check
```
GET /health
```
Returns server status and GPU availability.

### Load Models
```
POST /load-models
```
Explicitly load HuggingFace models. Models are auto-loaded on first transform request if not already loaded.

### Generate Prompt
```
POST /generate-prompt
Content-Type: application/json

{
    "client_name": "John Doe",
    "preferred_colors": "Warm neutrals, sage green",
    "likes": "Plants, natural light, minimalism",
    "dislikes": "Bold colors, clutter",
    "hobbies": "Reading, yoga, cooking",
    "requirements": "Home office space, storage solutions",
    "additional_comments": "Want a peaceful, zen-like atmosphere"
}
```

Returns:
```json
{
    "status": "success",
    "prompt": "...",
    "theme_info": {...}
}
```

### Transform Room
```
POST /transform
Content-Type: multipart/form-data

Form data:
- image: <image-file>
- client_data: <JSON>
- theme_info: <JSON>
```

Returns:
```json
{
    "status": "success",
    "image_base64": "...",
    "image_path": "/path/to/generated_images/...",
    "prompt_history": "/path/to/prompt_history/...",
    "theme": "theme_name",
    "timestamp": "timestamp"
}
```

### Get Prompt History
```
GET /prompt-history/<client_name>
```

Returns all saved prompts for a client.

### Retrieve Generated Image
```
GET /generated-images/<filename>
```

Returns the PNG image file.

## Workflow

### User Journey
1. Client fills the "Let's Know You Better" form
2. Submits form with room image
3. Frontend calls `/generate-prompt` endpoint
4. Design brief is generated and displayed
5. Client clicks "Generate Room Transformation"
6. Frontend calls `/transform` endpoint with image and preferences
7. Backend performs:
   - Depth map extraction using ControlNet
   - Image generation using Stable Diffusion
   - Saves generated image and prompt history
8. Generated image displayed in browser

### Prompt Generation Process

The service creates a detailed prompt including:
```
Transform this room into a [THEME] interior.

STYLE:
[Style description based on preferences]

COLOR PALETTE:
[User-selected colors]

MOOD:
Cozy, organized, welcoming

DESIGN ELEMENTS:
[Based on likes and hobbies]

RULES:
- Preserve room architecture
- Maintain furniture scale
- Declutter space
- Warm interior lighting

PERSONALIZATION:
Hobbies: [User's hobbies]
Requirements: [Space needs]

QUALITY:
- Professional interior photography
- Realistic perspective
- High resolution details
```

## Optimization

### GPU Memory Optimization
For cards with <12GB VRAM:

```python
# In image_service.py, modify the pipeline initialization:
self.pipeline.enable_attention_slicing()
```

### Faster Generation
```python
# Use fewer inference steps (trade quality for speed)
num_inference_steps=20  # Default: 30
```

### Model Quantization
For CPU inference with Intel Arc or AMD GPU:
```python
# Optional: torch.jit compilation, ONNX conversion
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 1 -b 0.0.0.0:5000 app:app --timeout 300 --max-requests 10
```

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM pytorch/pytorch:2.0-cuda11.8-runtime-ubuntu22.04
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app", "--timeout", "300"]
```

Build and run:
```bash
docker build -t interior-design-api .
docker run -p 5000:5000 --gpus all interior-design-api
```

### Environment Variables
```bash
export FLASK_ENV=production
export HUGGINGFACE_HUB_CACHE=/custom/path  # Custom model cache location
export API_PORT=5000
export MAX_FILE_SIZE=52428800  # 50MB in bytes
```

## Troubleshooting

### Out of Memory Error
**Solution:** Enable memory optimization
```python
self.pipeline.enable_attention_slicing()
# or use smaller image sizes: (512, 384)
```

### Models Not Downloading
**Solution:** Check internet connection and HuggingFace cache:
```bash
rm -rf ~/.cache/huggingface/hub/
# Then re-run to re-download
```

### CUDA Not Detected
**Solution:** Install PyTorch with correct CUDA version:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Slow Generation
**Solution:** Check:
1. GPU usage: `nvidia-smi`
2. Reduce image size in `image_service.py`
3. Reduce `num_inference_steps` parameter

## File Structure
```
interior-design-site/
├── app.py                    # Flask API server
├── image_service.py          # Image transformation service
├── script.js                 # Frontend JavaScript
├── styles.css                # Frontend styles
├── index.html                # Frontend HTML
├── requirements.txt          # Python dependencies
├── prompt_history/           # Saved design prompts (auto-created)
├── generated_images/         # Generated room images (auto-created)
└── uploads/                  # Temporary upload storage (auto-created)
```

## Performance Metrics

### Typical Generation Time (RTX 3060 12GB)
- Model Loading: ~30 seconds (first time only)
- Depth Extraction: ~2-3 seconds
- Image Generation (30 steps): ~25-30 seconds
- Total: ~30-35 seconds

### Typical File Sizes
- Input image: 1-5MB
- Generated image: 2-4MB
- Prompt history file: 5-10KB
- Model cache: ~9GB total

## Support & Development

### Adding Custom Models
Edit `image_service.py`:
```python
def load_models(self):
    # Replace pipeline model ID
    self.pipeline = StableDiffusionXLPipeline.from_pretrained(
        "model_hub_id"
    )
```

### Customizing Prompts
Edit `build_detailed_prompt()` method in `image_service.py` to modify the prompt template.

### API Authentication (Optional)
For production, add authentication:
```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

## License
This service integrates with open-source models from HuggingFace. Ensure compliance with their licenses.

## Next Steps
1. Set up the backend API on your server
2. Configure the frontend API_BASE_URL
3. Test the complete workflow
4. Deploy to production using Docker or your preferred hosting platform
