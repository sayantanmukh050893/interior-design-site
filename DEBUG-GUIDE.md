# API Connection Debugging Guide

## Quick Status Check

### ✓ What's Working
- ✅ Frontend server (http://localhost:8000) - HTTP server serving HTML, CSS, JS
- ✅ API server (http://localhost:5001) - Flask API
- ✅ `/health` endpoint - Returns server status
- ✅ `/generate-prompt` endpoint - Accepts POST requests with client data
- ✅ `/transform` endpoint - Accepts POST requests with image files
- ✅ CORS configuration - Properly configured to allow cross-origin requests
- ✅ All terminals tests - API working perfectly with curl and Python requests

## If You See a 404 Error in Browser

### What This Means
A 404 error typically means:
1. The page/endpoint cannot be found
2. The request is being sent to the wrong URL
3. The server is not running

### How to Debug

#### Step 1: Open Browser Developer Tools
1. Open http://localhost:8000 in your browser
2. Press `F12` or right-click → "Inspect" to open Developer Tools
3. Click the "Console" tab

#### Step 2: Check Console for Error Messages
You should see messages starting with `[Interior Design]` like:
- `[Interior Design] API Base URL: http://localhost:5001`
- `[Interior Design] Form submitted`
- `[Interior Design] Client Data: {...}`

#### Step 3: Look at Network Tab
1. Go to Developer Tools → "Network" tab
2. Fill out the form and submit it
3. Look for a request to `localhost:5001/generate-prompt`
4. Click on it to see:
   - **Status Code**: Should be 200
   - **Method**: Should be POST
   - **Request Headers**: Should include `Content-Type: application/json`
   - **Response**: Should contain the design brief

## Manual API Test from Browser

### Simple Test (Copy-Paste into Console)

```javascript
// Test the /health endpoint
fetch('http://localhost:5001/health')
    .then(r => r.json())
    .then(data => console.log('✓ Health check passed:', data))
    .catch(err => console.error('✗ Health check failed:', err));

// Test the /generate-prompt endpoint
fetch('http://localhost:5001/generate-prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "Test",
        email: "test@example.com",
        about: "Test",
        preferred_colors: "Blue",
        likes: "Modern",
        dislikes: "Clutter",
        hobbies: "Reading",
        requirements: "Bright",
        additional_comments: "Test"
    })
})
    .then(r => {
        console.log('Status:', r.status);
        return r.json();
    })
    .then(data => console.log('✓ Generate prompt successful:', data))
    .catch(err => console.error('✗ Generate prompt failed:', err));
```

## Terminal Commands for Testing

### Check if servers are running
```bash
# Check what's listening on ports 8000 and 5001
netstat -tlnp | grep -E "8000|5001"
# or
lsof -i :8000
lsof -i :5001
```

### Test API with curl
```bash
# Test health endpoint
curl http://localhost:5001/health

# Test generate-prompt
curl -X POST http://localhost:5001/generate-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "preferred_colors": "Blue",
    "likes": "Modern",
    "dislikes": "Clutter",
    "hobbies": "Reading",
    "requirements": "Bright",
    "additional_comments": "Test"
  }'
```

### Test with Python
```bash
python3 << 'EOF'
import requests

API = 'http://localhost:5001'

# Test health
r = requests.get(f'{API}/health')
print(f"Health: {r.status_code}")

# Test generate-prompt
r = requests.post(f'{API}/generate-prompt', json={
    "name": "Test",
    "preferred_colors": "Blue",
    "likes": "Modern",
    "dislikes": "Clutter",
    "hobbies": "Reading",
    "requirements": "Bright",
    "additional_comments": "Test"
})
print(f"Generate Prompt: {r.status_code}")
EOF
```

## Common Issues and Solutions

### Issue: Browser shows 404, but curl works
**Cause**: Usually CORS or method mismatch
**Solution**:
1. Check browser console for detailed error messages
2. Verify the request is using POST (not GET)
3. Verify the Content-Type header is set to 'application/json'

### Issue: Network tab shows no request at all
**Cause**: JavaScript error preventing the fetch call
**Solution**:
1. Check browser console for JavaScript errors
2. Look for `[Interior Design]` prefix in console logs
3. Verify form fields have correct `name` attributes

### Issue: Request hangs/never completes
**Cause**: API server might be processing a heavy task or unresponsive
**Solution**:
1. Check terminal where API is running for error messages
2. Try the `/health` endpoint first to verify server is responsive
3. Restart the API server if needed

## Additional Debugging

### Enable More Detailed Logging
The frontend now includes comprehensive logging. Check browser console for:
- Form submission tracking
- API request details
- Response status and headers
- Detailed error messages

### Check Server Logs
Terminal where Flask API is running should show:
```
 * Running on http://127.0.0.1:5001
127.0.0.1 - - [date time] "POST /generate-prompt HTTP/1.1" 200 -
```

If you see 405 METHOD NOT ALLOWED, it means the route exists but doesn't support that HTTP method.

## File Locations

- **Frontend**: `/workspaces/interior-design-site/index.html`
- **Frontend Logic**: `/workspaces/interior-design-site/script.js`
- **Frontend Styles**: `/workspaces/interior-design-site/styles.css`
- **API Server**: `/workspaces/interior-design-site/app.py`
- **Image Service**: `/workspaces/interior-design-site/image_service.py`

## Quick Fix Checklist

- [ ] Both servers are running (8000 and 5001)
- [ ] Browser console shows `[Interior Design] API Base URL: http://localhost:5001`
- [ ] Network tab shows POST request to `/generate-prompt`
- [ ] Response status is 200
- [ ] Response contains "prompt" and "theme_info" fields
- [ ] No JavaScript errors in console
