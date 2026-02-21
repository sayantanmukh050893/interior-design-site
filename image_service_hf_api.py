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
        
        # Get API token from environment (optional but recommended)
        self.api_token = os.getenv("HF_API_TOKEN", None)
        
        # Hugging Face API endpoint
        self.api_base_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        
        # Available models in order of preference (text-to-image)
        # FLUX.2-klein-9B is the primary model, with fallback options
        self.models = [
            "black-forest-labs/FLUX.2-klein-9B",
            "black-forest-labs/FLUX.1-dev",
            "stabilityai/stable-diffusion-3-medium",
            "stabilityai/stable-diffusion-xl-base-1.0"
        ]
        self.current_model_idx = 0
        self.model = self.models[0]
        
        # Status
        self.device = "api"
        
        if not self.api_token:
            print("⚠️ Warning: HF_API_TOKEN not set. API calls may be rate-limited.")
            print("Set HF_API_TOKEN environment variable for better performance.")
            print("Get your token from https://huggingface.co/settings/tokens")
    
    def load_models(self):
        """No-op: Models are loaded on HF servers"""
        print(f"Using Hugging Face Inference API - model: {self.model} (FLUX.2-klein-9B)")
    
    def build_detailed_prompt(self, client_data, theme_info):
        """Build transformation prompt for FLUX text-to-image model"""
        
        prompt = f"""Professional interior design photograph of a {theme_info.get('theme_name', 'Modern')} {client_data.get('room_type', 'living room')}.

DESIGN STYLE: {theme_info.get('style_description', 'Contemporary and sophisticated')}
COLOR PALETTE: {theme_info.get('color_palette', 'Neutral tones with warm accents')}
ROOM DIMENSIONS: {client_data.get('room_length', 'Standard')} feet x {client_data.get('room_width', 'Standard')} feet

KEY DESIGN FEATURES:
- {client_data.get('likes', 'Well-organized and spacious layout')}
- Natural and ambient lighting
- Premium furniture and decoration
- Professional interior styling
- High-end design finish
- Photorealistic, magazine-quality photography
- 8K resolution, sharp details
- Architectural digest quality"""
        
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
        Transform room using text-to-image via Hugging Face Inference API
        Uses multi-model fallback strategy for reliability
        
        Args:
            image: PIL Image or image path (input reference image)
            client_data: dict with client preferences
            theme_info: dict with theme details
        
        Returns:
            dict with transformation result
        """
        
        try:
            # Load reference image (used for context, not direct transformation)
            if isinstance(image, str):
                ref_image = Image.open(image).convert("RGB")
            else:
                ref_image = image.convert("RGB")
            
            # Build prompt for text-to-image generation
            full_prompt = self.build_detailed_prompt(client_data, theme_info)
            
            print(f"\nGenerating interior design using FLUX.2-klein-9B...")
            print(f"Prompt: {full_prompt[:100]}...")
            
            # Try different models with fallback
            result_image = None
            for idx, model in enumerate(self.models, 1):
                print(f"\n[Strategy {idx}] Trying {model}...")
                self.current_model_idx = idx - 1
                self.model = model
                
                result_image = self._call_text_to_image(full_prompt)
                
                if result_image is not None:
                    print(f"✅ Success with {model}!")
                    break
                else:
                    if idx < len(self.models):
                        print(f"⚠️ {model} failed, trying next model...")
            
            # If all API models fail, use local transformer
            if result_image is None:
                print("\n⚠️ All API models failed (including FLUX.2-klein-9B). Using local style transformer...")
                local_transformer = LocalImageTransformer()
                result_image = local_transformer._apply_style_transform(ref_image, theme_info)
                model_used = "Local Style Transform"
            else:
                model_used = f"FLUX.2-klein-9B ({self.model})" if "FLUX" in self.model else f"Fallback Model ({self.model})"
            
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
                "model": model_used
            }
            
        except Exception as e:
            print(f"Error in transform_room: {str(e)}")
            raise
    
    def _call_text_to_image(self, prompt):
        """Call FLUX.2-klein-9B text-to-image model via HF Inference API"""
        try:
            url = f"{self.api_base_url}/{self.model}"
            
            # Prepare JSON payload for text-to-image
            payload = {
                "inputs": prompt
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            print(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Response is image binary
                result_image = Image.open(BytesIO(response.content))
                return result_image
            else:
                status_desc = response.text[:100] if response.text else "Unknown error"
                print(f"❌ Error {response.status_code}: {status_desc}")
                return None
            
        except Exception as e:
            print(f"❌ Error calling {self.model}: {str(e)}")
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
