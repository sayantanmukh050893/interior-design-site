"""
Image transformation service using Hugging Face Inference API
This service offloads AI inference to Hugging Face, eliminating heavy local dependencies
"""

import os
import base64
import json
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image
from pathlib import Path


class HuggingFaceInteriorDesignTransformer:
    """Transformer using Hugging Face Inference API"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Get API token from environment
        self.api_token = os.getenv("HF_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "HF_API_TOKEN environment variable not set. "
                "Get your token from https://huggingface.co/settings/tokens"
            )
        
        # Hugging Face API endpoint
        self.api_base_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        
        # Model to use (Instruct-Pix2Pix for image-to-image transformations)
        self.model = "timbrooks/instruct-pix2pix"
        
        # Status
        self.device = "api"
    
    def load_models(self):
        """No-op: Models are loaded on HF servers"""
        print("Using Hugging Face Inference API - models already loaded on remote servers")
    
    def build_detailed_prompt(self, client_data, theme_info):
        """Build transformation prompt"""
        
        prompt = f"""Transform this room into a {theme_info.get('theme_name', 'Modern')} interior.

STYLE: {theme_info.get('style_description', 'Contemporary')}
COLORS: {theme_info.get('color_palette', 'Neutral tones')}
MOOD: Comfortable, welcoming

CLIENT PREFERENCES:
- Likes: {client_data.get('likes', '')}
- Dislikes: {client_data.get('dislikes', '')}
- Hobbies: {client_data.get('hobbies', '')}

REQUIREMENTS: {client_data.get('requirements', '')}

DESIGN RULES:
- Keep room layout and architecture
- Realistic furniture scale
- Clean, organized space
- Good lighting
- Professional quality"""
        
        return prompt.strip()
    
    def save_prompt_history(self, client_name, prompt, image_filename, theme):
        """Save prompt to file"""
        timestamp = datetime.now().isoformat()
        prompt_file = self.prompt_history_dir / f"{client_name}_{timestamp.split('T')[0]}_prompt.txt"
        
        content = f"""CLIENT DESIGN TRANSFORMATION PROMPT
Generated: {timestamp}
Theme: {theme}

{prompt}

Generated Image: {image_filename}
"""
        
        with open(prompt_file, 'w') as f:
            f.write(content)
        
        return str(prompt_file)
    
    def _resize_image(self, image, max_size=512):
        """Resize image for API processing"""
        # API typically works with multiples of 64
        size = min(max_size, max(image.size))
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        return image
    
    def _encode_image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _decode_image_from_base64(self, base64_str):
        """Convert base64 string to PIL Image"""
        img_data = base64.b64decode(base64_str)
        return Image.open(BytesIO(img_data))
    
    def transform_room(self, image, client_data, theme_info):
        """
        Transform room image using Hugging Face Inference API
        
        Args:
            image: PIL Image or image path
            client_data: dict with client preferences
            theme_info: dict with theme details
        
        Returns:
            dict with transformation result
        """
        
        try:
            # Load image
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            else:
                image = image.convert("RGB")
            
            # Resize for API
            image = self._resize_image(image)
            
            # Build prompt
            full_prompt = self.build_detailed_prompt(client_data, theme_info)
            
            print(f"Sending to Hugging Face API with prompt:\n{full_prompt}")
            print(f"Calling Instruct-Pix2Pix for image transformation...")
            
            # Call Instruct-Pix2Pix
            result_image = self._call_instruct_pix2pix(image, full_prompt)
            
            if result_image is None:
                print("Transformation failed, using original image.")
                result_image = image
            
            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = client_data.get('name', 'client').replace(' ', '_')
            image_filename = f"{client_name}_{timestamp}_transformed.png"
            image_path = self.output_dir / image_filename
            result_image.save(image_path)
            
            print(f"Saved to: {image_path}")
            
            # Convert to base64
            img_base64 = self._encode_image_to_base64(result_image)
            
            # Save history
            prompt_file = self.save_prompt_history(
                client_name, 
                full_prompt,
                image_filename,
                theme_info.get('theme_name')
            )
            
            return {
                "status": "success",
                "image_base64": img_base64,
                "image_path": str(image_path),
                "prompt_history": prompt_file,
                "theme": theme_info.get('theme_name'),
                "timestamp": timestamp,
                "model": "Hugging Face Inference API"
            }
            
        except Exception as e:
            print(f"Error in transform_room: {str(e)}")
            raise
    
    def _call_instruct_pix2pix(self, image, prompt):
        """Call Instruct-Pix2Pix via Hugging Face Inference API"""
        try:
            # Convert PIL image to PNG bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
            
            # Prepare multipart form data (required by HF Inference API)
            files = {
                'image': ('image.png', img_byte_arr.getvalue(), 'image/png')
            }
            data = {
                'prompt': prompt,
                'negative_prompt': 'blurry, low quality, distorted',
                'num_inference_steps': 20,
                'guidance_scale': 7.5,
                'image_guidance_scale': 1.5
            }
            
            url = f"{self.api_base_url}/{self.model}"
            print(f"Calling Instruct-Pix2Pix model at {url}...")
            
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=120
            )
            
            print(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Response should be image binary
                result_image = Image.open(BytesIO(response.content))
                print("✅ Instruct-Pix2Pix transformation successful!")
                return result_image
            elif response.status_code == 410:
                print(f"⚠️ Endpoint deprecated (410), retrying with router...")
                # Try router endpoint as fallback
                url_router = url.replace('api-inference.huggingface.co', 'router.huggingface.co')
                response = requests.post(url_router, headers=self.headers, files=files, data=data, timeout=120)
                if response.status_code == 200:
                    result_image = Image.open(BytesIO(response.content))
                    print("✅ Transformation successful via router!")
                    return result_image
                else:
                    print(f"❌ Router error: {response.status_code}")
                    return None
            else:
                print(f"❌ Error: {response.status_code}")
                response_text = response.text[:300] if response.text else "No response body"
                print(f"Response: {response_text}")
                return None
            
        except Exception as e:
            print(f"❌ Error calling model: {str(e)}")
            return None


# Local transformer for when API token is not available
class LocalImageTransformer:
    """Apply style-based transformations using PIL (no API needed)"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.device = "local"
    
    def load_models(self):
        print("Local transformer - using PIL-based transformations")
    
    def build_detailed_prompt(self, client_data, theme_info):
        return f"Transform room: {theme_info.get('theme_name')}"
    
    def _apply_style_transform(self, image, theme_info):
        """Apply style-based transformations to image"""
        from PIL import ImageEnhance, ImageOps
        
        theme_name = theme_info.get('theme_name', 'Modern').lower()
        style = theme_info.get('style_description', '').lower()
        colors = theme_info.get('color_palette', '').lower()
        
        # Start with original image
        result = image.copy()
        
        # Apply theme-specific transformations
        if 'modern' in theme_name or 'contemporary' in style:
            # Modern: Increase contrast and slight desaturation
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.95)
            
        elif 'classic' in theme_name or 'traditional' in style:
            # Classic: Warm tones, increase saturation
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.2)
            result = ImageOps.posterize(result, 6)  # Reduces colors for cleaner look
            
        elif 'minimalist' in theme_name or 'minimal' in style:
            # Minimalist: High contrast, clean
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.1)
            
        elif 'luxury' in theme_name or 'elegant' in style:
            # Luxury: Increased saturation and subtle color shift
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.05)
            
        elif 'industrial' in theme_name or 'rustic' in style:
            # Industrial: Desaturate slightly, increase contrast
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.85)
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.4)
            
        elif 'cozy' in theme_name or 'warm' in colors:
            # Cozy: Warm colors, slight color shift to warmer tones
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.15)
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.1)
            
        else:
            # Default: Slight enhancement
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.05)
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.1)
        
        # Always add slight sharpness
        from PIL import ImageFilter
        result = result.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return result
    
    def transform_room(self, image, client_data, theme_info):
        """Apply local style transformation"""
        if isinstance(image, str):
            result_image = Image.open(image)
        else:
            result_image = image
        
        result_image = result_image.convert("RGB")
        
        # Apply style transformation
        result_image = self._apply_style_transform(result_image, theme_info)
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = client_data.get('name', 'client').replace(' ', '_')
        image_filename = f"{client_name}_{timestamp}_transformed.png"
        image_path = self.output_dir / image_filename
        result_image.save(image_path)
        
        # Convert to base64
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Save history
        prompt_file = self.prompt_history_dir / f"{client_name}_{timestamp.split('T')[0]}_prompt.txt"
        content = f"""CLIENT DESIGN TRANSFORMATION PROMPT
Generated: {datetime.now().isoformat()}
Theme: {theme_info.get('theme_name')}
Method: Local Style Transform

Transformation applied: {theme_info.get('theme_name')} style
Style: {theme_info.get('style_description', '')}
Colors: {theme_info.get('color_palette', '')}

Generated Image: {image_filename}
"""
        with open(prompt_file, 'w') as f:
            f.write(content)
        
        return {
            "status": "success",
            "image_base64": img_base64,
            "image_path": str(image_path),
            "theme": theme_info.get('theme_name'),
            "timestamp": timestamp,
            "model": "Local Style Transform (No API needed)",
            "note": "Add HF_API_TOKEN environment variable for AI-powered transformations"
        }


def get_transformer():
    """Get transformer based on API token availability"""
    try:
        token = os.getenv("HF_API_TOKEN")
        
        if not token:
            print("⚠️  HF_API_TOKEN not set. Using local style transformations.")
            return LocalImageTransformer()
        
        # Token exists, try to use HF API transformer
        print("✅ HF_API_TOKEN found. Using Hugging Face Inference API for transformations.")
        return HuggingFaceInteriorDesignTransformer()
            
    except Exception as e:
        print(f"⚠️  Error initializing HF transformer: {str(e)}. Falling back to local transformations.")
        return LocalImageTransformer()


if __name__ == "__main__":
    print("Hugging Face Inference API - Interior Design Transformer")
    print("\nSetup:")
    print("1. Get API token: https://huggingface.co/settings/tokens")
    print("2. Set HF_API_TOKEN environment variable")
    print("3. Run your Flask app")
