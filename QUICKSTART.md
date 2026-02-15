# Quick Start Guide - Image Transformation Service

## 5-Minute Setup

### Prerequisites
- Python 3.8+
- NVIDIA GPU with CUDA support (optional but recommended)

### Quick Install
```bash
# 1. Clone and navigate
cd interior-design-site

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start API server
python app.py

# 5. In another terminal, serve frontend
python -m http.server 8000

# 6. Open browser
# Frontend: http://localhost:8000
# API: http://localhost:5000
```

## Using the Service

### Step 1: Fill the Form
- Go to "Design Brief" section
- Fill in your preferences:
  - Name & Email
  - About yourself
  - Color preferences
  - Likes/Dislikes
  - Hobbies
  - Space requirements

### Step 2: Upload Room Image
- Upload a clear photo of the room you want to transform
- Supported formats: JPG, PNG, WebP, GIF
- Max size: 50MB

### Step 3: Generate Design Brief
- Click "Generate Design Brief"
- Review your personalized design prompt

### Step 4: Transform Room
- Click "Generate Room Transformation"
- Wait for AI to transform your room (typically 30-40 seconds)
- View and download your transformed room image

## API Examples

### Using cURL

#### Generate Prompt
```bash
curl -X POST http://localhost:5000/generate-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Jane Doe",
    "preferred_colors": "Soft pastels, cream",
    "likes": "Minimalist, clean lines, plants",
    "dislikes": "Clutter, dark colors",
    "hobbies": "Painting, reading",
    "requirements": "Home gallery space"
  }'
```

#### Transform Room Image
```bash
curl -X POST http://localhost:5000/transform \
  -F "image=@room.jpg" \
  -F 'client_data={"name":"Jane","preferred_colors":"Soft pastels"}' \
  -F 'theme_info={"theme_name":"Minimalist"}' \
  > result.json
```

### Using Python

```python
import requests
import json

# Generate prompt
response = requests.post(
    'http://localhost:5000/generate-prompt',
    json={
        'client_name': 'John',
        'preferred_colors': 'Blues and greens',
        'likes': 'Modern, plants',
        'dislikes': 'Traditional',
        'hobbies': 'Photography',
        'requirements': 'Good lighting'
    }
)
print(response.json())

# Transform image
with open('room.jpg', 'rb') as f:
    files = {
        'image': f,
        'client_data': json.dumps({'name': 'John', 'preferred_colors': 'Blues'}),
        'theme_info': json.dumps({'theme_name': 'Modern'})
    }
    response = requests.post(
        'http://localhost:5000/transform',
        files=files
    )
print(response.json())
```

## Checking Server Status

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Interior Design Image Transformation",
  "gpu_available": true
}
```

## Generated Files

After transformation, check these directories:

### Prompt History
```
prompt_history/
├── client_name_2024-02-15_prompt.txt
├── client_name_2024-02-16_prompt.txt
...
```

### Generated Images
```
generated_images/
├── client_name_20240215_120530_transformed.png
├── client_name_20240215_130045_transformed.png
...
```

## Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Use different port
python app.py --port 8080
```

### GPU not detected
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Install correct PyTorch CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Slow generation
- Ensure GPU is being used (check nvidia-smi)
- Use smaller images
- Reduce inference steps

### Out of memory
```python
# Add to image_service.py load_models():
self.pipeline.enable_attention_slicing()
```

## Environment Variables

```bash
# Optional configuration
export FLASK_ENV=production
export FLASK_DEBUG=0
export MAX_FILE_SIZE=52428800
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| CORS errors | Add `--cors` flag or check API_BASE_URL in script.js |
| Models not found | First run downloads ~9GB, requires internet |
| Timeout errors | Increase Flask timeout or reduce image size |
| Poor results | Adjust prompt in image_service.py build_detailed_prompt() |

## Next Steps

1. **Customize Prompts**: Edit `build_detailed_prompt()` in `image_service.py`
2. **Add Styling**: Modify CSS in `styles.css`
3. **Deploy**: Use Docker or your hosting platform
4. **Integrate CMS**: Connect to your backend database

## Resources

- [Stable Diffusion Docs](https://huggingface.co/docs/diffusers/)
- [ControlNet Guide](https://github.com/lllyasviel/ControlNet)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [HuggingFace Hub](https://huggingface.co/)

## Support

For issues:
1. Check logs: `grep "Error" app.py output`
2. Review IMAGE-TRANSFORMATION-GUIDE.md for detailed setup
3. Check Flask server status: `curl http://localhost:5000/health`
