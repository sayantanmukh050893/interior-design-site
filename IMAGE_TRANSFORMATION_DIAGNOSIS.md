# Image Transformation Service - Diagnosis & Setup

## Current Status

### ✅ What's Working
- **Flask Backend Running**: Python Flask app is active on port **5001** (not 5000)
- **Endpoints Available**:
  - `/transform` - Main image transformation endpoint  
  - `/generate-prompt` - Generates design prompts from form data
  - `/health` - Health check endpoint
- **Frontend Form**: "Let's Know You Better" form is fully functional

### ❌ The Problem: "Page Refreshes Instead of Returning Image"

The issue is likely due to:

1. **Incorrect API URL in Frontend**: The JavaScript assumes the backend is on the same domain (`window.location.origin`), but:
   - If running on a different port (5001 vs 3000/8000), the fetch fails
   - CORS issues may prevent cross-origin requests

2. **Missing Backend Response Handling**: After form submission, if the `/transform` endpoint fails silently, the page refreshes

3. **No Error Logging on Frontend**: Errors aren't being displayed to the user

## Architecture Overview

### Frontend Flow (script.js)
```
User fills form → Submit Button
  ↓
knowBetterForm event listener
  ↓
1. Call /generate-prompt → Get AI-generated design prompt
  ↓
2. Call performImageTransformation()
  ↓
3. Call /transform endpoint with:
   - Image file
   - Client data (JSON)
   - Generated prompt
  ↓
4. Display transformed image in slider
```

### Backend Flow (app.py)
```
POST /transform
  ↓
Receive image + form data
  ↓
Initialize FLUXTransformer (from image_service_flux_multi.py)
  ↓
Use FLUX.2-klein-9B model via:
  - HuggingFace Router API (if token available)
  - OR Gradio Direct Call (fallback)
  - OR Mock image (testing)
  ↓
Return transformed image as base64 JSON
```

### Image Service Files

| File | Purpose | Status |
|------|---------|--------|
| `image_service_flux_multi.py` | Main transformer with fallback strategies | ✅ Active |
| `image_service_hf_api.py` | Direct HuggingFace API integration | Backup |
| `image_service_gradio_space.py` | Gradio Space endpoint | Backup |
| `image_service_flux_multi.py` | Lightweight version | Fallback |

**Current**: Using `image_service_flux_multi.py` (imported in app.py)

## Why Image Isn't Returning

### Possible Root Causes

1. **Backend Not Initialized Properly**
   ```python
   # app.py line 20
   transformer = FLUXTransformer()  # May fail silently
   if transformer is None:
       # No error is logged to frontend
   ```

2. **Missing HuggingFace API Token**
   - **Location**: `.env` file
   - **Required**: Set `HF_API_TOKEN='your_token_here'`
   - **Without it**: Falls back to Gradio Space (slower, rate-limited)

3. **API Rate Limiting/Timeout**
   - FLUX.2-klein-9B is resource-intensive
   - Takes 1-10 minutes for transformation
   - May timeout or get rate-limited

4. **Browser CORS/Network Issues**
   - Check Developer Tools → Network tab
   - Look for failed fetch requests

## Solutions

### Solution 1: Verify Backend Connectivity (Immediate)

**Test the `/health` endpoint:**
```bash
curl http://localhost:5001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Interior Design Image Transformation",
  "gpu_available": false
}
```

### Solution 2: Check HuggingFace API Token

**Check if token is set:**
```bash
echo $HF_API_TOKEN
```

**If not set, add to `.env`:**
```env
HF_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"
```

**Get token from**: https://huggingface.co/settings/tokens

### Solution 3: Add Error Logging to Frontend

**Update JavaScript to show backend errors:**
```javascript
// In script.js, inside performImageTransformation()
if (!response.ok) {
    const errorData = await response.text();
    console.error('Transform Error:', errorData);
    showNotification(`Error: ${errorData}`, 'error');  // ← Show error to user
    throw new Error(`Transformation failed: ${response.status}`);
}
```

### Solution 4: Update API URL

**In script.js (line 112):**
```javascript
// Current (may fail if ports differ)
const API_BASE_URL = window.location.origin;

// Better approach for local development:
const API_BASE_URL = window.location.protocol + '//' + 
                     window.location.hostname + ':5001';
```

## Testing Checklist

- [ ] Backend is running: `ps aux | grep app.py`
- [ ] Backend is accessible: `curl http://localhost:5001/health`
- [ ] HF_API_TOKEN is set: `echo $HF_API_TOKEN`
- [ ] Check browser console (F12) for errors
- [ ] Check Firefox/Chrome Network tab for failed requests
- [ ] Test with small image file (<5MB)
- [ ] Allow 2-5 minutes for transformation to complete

## Recommended Next Steps

1. **Check server logs** for specific error messages
2. **Update .env** with valid HuggingFace API token
3. **Add better error messages** to frontend
4. **Increase timeout** if transformations are taking too long
5. **Test with mock/lightweight service** first before full FLUX model
