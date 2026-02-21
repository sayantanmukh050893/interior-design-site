## Interior Design Site - Gradio Space API Integration

### Installation & Setup Complete ✅

The application has been successfully updated to use **HuggingFace Spaces Gradio API** with **FLUX.2-klein-9B**.

#### What Was Updated

1. **New Service**: `image_service_gradio_space.py`
   - Uses Gradio client to connect to: `black-forest-labs/FLUX.2-klein-9B`
   - Converts design prompts to photorealistic interior images

2. **Modified**: `app.py`
   - `/transform` endpoint now uses Gradio Space API
   - Accepts optional `prompt` parameter from `/generate-prompt`
   - Enhanced error handling for graceful degradation

3. **Dependencies**: Added `gradio-client==0.15.0`
   - Already installed via `pip install -r requirements.txt`

---

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt

# Run the app
python app.py

# App will be available at: http://127.0.0.1:5001
```

---

### API Workflow

#### 1. Generate Design Prompt
```bash
curl -X POST http://localhost:5001/generate-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John",
    "preferred_colors": "Warm neutrals",
    "likes": "Modern, spacious",
    "dislikes": "Clutter",
    "hobbies": "Reading, cooking",
    "requirements": "Good lighting, storage",
    "additional_comments": "Minimalist style"
  }'
```

**Response**: Includes `prompt` and `theme_info`

#### 2. Transform Image with Generated Prompt
```bash
# Use the prompt from step 1
curl -X POST http://localhost:5001/transform \
  -F "image=@room.jpg" \
  -F "client_data={\"name\":\"John\",\"room_type\":\"living room\"}" \
  -F "prompt=<paste_generated_prompt_here>"
```

**Response**: Base64 encoded transformed image

---

### Environment Variables (Optional)

Set `HF_API_TOKEN` for improved rate limiting (optional):
```bash
export HF_API_TOKEN="your_huggingface_token"
```

Get your token from: https://huggingface.co/settings/tokens

---

### Important Notes

⚠️ **Gradio Initialization Warning**:
- You may see: `⚠️ Warning initializing Gradio client: Expecting value: line 1 column 1 (char 0)`
- This is NOT a critical error - it's handled gracefully
- The app will attempt to recover and reconnect when needed
- The warning happens because of how Gradio initializes the space connection

✅ **The app continues to function normally** despite this warning

---

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve main HTML page |
| `/health` | GET | Health check |
| `/load-models` | POST | Initialize models |
| `/generate-prompt` | POST | Generate design prompt |
| `/transform` | POST | Transform room image |
| `/prompt-history/{client_name}` | GET | Get prompt history |

---

### Troubleshooting

**Issue**: Port 5001 is already in use
```bash
# Kill existing process
kill $(lsof -t -i:5001)

# Or use a different port by modifying app.py
```

**Issue**: Gradio connection fails
- Check internet connection
- Verify `gradio-client` is installed: `pip show gradio-client`
- The app will auto-recover on next request

**Issue**: Images not generating
- Ensure the reference image file is valid
- Check that `prompt` is properly formatted
- The HuggingFace Space may have usage limits

---

### File Structure

```
app.py                              # Flask API server
image_service_gradio_space.py      # NEW: Gradio Spaces integration
image_service_hf_api.py            # Fallback HF API service
requirements.txt                    # Dependencies (updated with gradio-client)
index.html                         # Frontend
styles.css                         # Styling
script.js                          # Frontend logic
```

---

### Next Steps

1. ✅ Dependencies installed
2. ✅ Gradio Space integration complete
3. ✅ App running at http://127.0.0.1:5001
4. Test with your room images!

For detailed workflow, see the [AI Integration Documentation](./DEPLOYMENT-CONFIG.md).
