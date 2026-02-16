# Hugging Face API Migration Guide

This project has been migrated to use **Hugging Face Inference API** instead of running heavy AI models locally. This significantly reduces:

- ⚡ CPU/GPU resource usage
- 📦 Dependency footprint (from ~2GB to ~100MB)
- ⏱️ Cold start time
- 💾 Storage requirements

## What Changed

| Aspect | Before | After |
|--------|--------|-------|
| Model Size | ~2-5 GB | 0 bytes (cloud-based) |
| Dependencies | PyTorch, Diffusers, Transformers | Requests, Flask |
| Setup Time | 30+ minutes | < 2 minutes |
| Memory Usage | 2-8 GB RAM | < 300 MB |
| GPU Required | Recommended | Optional |
| Runtime | Local inference (slow on CPU) | Cloud API (fast, reliable) |

## Setup Instructions

### 1. Get Hugging Face API Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new **User Access Token** (read-only is fine)
3. Accept Hugging Face model licenses if prompted

### 2. Configure Token

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your token:

```
HF_API_TOKEN=hf_your_actual_token_here
```

**Or** set the environment variable directly:

```bash
export HF_API_TOKEN=hf_your_token_here
```

### 3. Install Lightweight Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The app will:
- ✅ Use Hugging Face API if `HF_API_TOKEN` is set
- ⚠️ Use mock mode if token is not set (no real transformations)

## API Models Used

### Image-to-Image Transformation
- **Model**: `timbrooks/instruct-pix2pix`
- **Use**: Transforms rooms based on text instructions and input image
- **Speed**: ~30-60 seconds per image (depends on queue)
- **Quality**: High-quality professional results

### Text-to-Image Generation (Future)
- **Model**: `stabilityai/stable-diffusion-2-1`
- **Use**: Can generate design reference images

## Usage Examples

### Transform a Room Image

```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('client_data', JSON.stringify({
    name: 'John Doe',
    likes: 'minimalist, clean spaces',
    dislikes: 'clutter',
    hobbies: 'reading, art',
    requirements: 'good natural lighting'
}));
formData.append('theme_info', JSON.stringify({
    theme_name: 'Modern Minimalist',
    style_description: 'Contemporary with clean lines',
    color_palette: 'whites, grays, blacks'
}));

const response = await fetch('/transform', {
    method: 'POST',
    body: formData
});

const result = await response.json();
```

## Pricing

Hugging Face Inference API offers:
- **Free tier**: Limited requests per month
- **Pro tier**: $9/month for higher rate limits
- **Enterprise**: Custom pricing for high-volume users

Each inference typically costs very little (fractions of a cent).

## Troubleshooting

### "HF_API_TOKEN environment variable not set"

**Solution**: Set your Hugging Face API token:
```bash
export HF_API_TOKEN=hf_your_token
```

### API Rate Limit Exceeded

**Solution**: 
- Upgrade to Hugging Face Pro: https://huggingface.co/pricing
- Or wait a few hours for the rate limit to reset

### "API Error: 429"

This means the model is under high load. The API will auto-retry. Just wait a moment and try again.

### "API Error: 403"

Your token might be invalid or expired. Get a new one from https://huggingface.co/settings/tokens

## Performance Notes

- **First request**: May take 30-60 seconds (model loading on HF servers)
- **Subsequent requests**: 20-40 seconds (faster model inference)
- **Inference time** varies based on:
  - Model queue load
  - Image size
  - Network latency
  - Time of day (fewer requests = faster responses)

## Benefits Over Local Inference

✅ **No GPU required** - Works on any Codespace
✅ **Instant scalability** - Handle multiple requests simultaneously
✅ **Always up-to-date** - Models update automatically
✅ **Zero maintenance** - No model downloading or compatibility issues
✅ **Cost-effective** - Pay only for what you use
✅ **Reliable** - 99.9% uptime SLA

## Migration from Local Models

If you previously used local models and want to keep that option:

1. **Local mode** is still available in `image_service_lightweight.py`
2. To use local models: Edit `app.py` and import from `image_service_lightweight`
3. This requires PyTorch and Diffusers (see old requirements.txt)

## Future Enhancements

- [ ] Add support for ControlNet models (more precise transformations)
- [ ] Implement caching for identical requests
- [ ] Add websocket support for live transformation progress
- [ ] Support multiple model providers (Replicate, Together AI, etc.)
- [ ] Add cost tracking dashboard

## Support

For issues with:
- **Hugging Face API**: https://github.com/huggingface/hub-docs
- **This project**: Check the README.md or create an issue
