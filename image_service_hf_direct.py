"""
Image transformation service using HuggingFace Inference APIwith direct REST calls
Uses black-forest-labs/FLUX.2-klein-9B model via HuggingFace Inference API
"""

import os
import base64
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image
from pathlib import Path


class HFDirectInteriorDesignTransformer:
    """Transformer using HuggingFace Inference API with direct REST calls"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Get API token from environment (optional)
        self.api_token = os.getenv("HF_API_TOKEN", None)
        
        # FLUX.2-klein-9B model endpoint (using new router)
        self.model_id = "black-forest-labs/FLUX.2-klein-9B"
        # Updated to use new HuggingFace router endpoint
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        
        # Prepare headers
        self.headers = {"Content-Type": "application/json"}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
        
        self.device = "api"
        
        if not self.api_token:
            print("⚠️ Warning: HF_API_TOKEN not set. API calls may be rate-limited.")
            print("Set HF_API_TOKEN environment variable for better performance: https://huggingface.co/settings/tokens")
    
    def load_models(self):
        """No-op: Models are available via HuggingFace API"""
        print(f"Using HuggingFace Inference API: {self.model_id}")
    
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
- 4K resolution, sharp details
- Interior design inspiration quality"""
        
        return prompt.strip()
    
    def save_prompt_history(self, client_name, prompt, image_filename, theme):
        """Save prompt to file"""
        timestamp = datetime.now().isoformat()
        prompt_file = self.prompt_history_dir / f"{client_name}_{timestamp.split('T')[0]}_prompt.txt"
        
        content = f"""CLIENT DESIGN TRANSFORMATION PROMPT
Generated: {timestamp}
Theme: {theme}
Model: FLUX.2-klein-9B (HuggingFace Inference API)

{prompt}

Generated Image: {image_filename}
"""
        
        with open(prompt_file, 'w') as f:
            f.write(content)
        
        return str(prompt_file)
    
    def _encode_image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _call_text_to_image_api(self, prompt):
        """Call FLUX.2-klein-9B via HuggingFace Inference API"""
        try:
            print(f"\n🚀 Calling FLUX.2-klein-9B via HuggingFace Inference API...")
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Prepare request payload
            payload = {"inputs": prompt}
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            print(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Response is image binary
                result_image = Image.open(BytesIO(response.content))
                return result_image
            elif response.status_code == 503:
                # Model is loading
                print("⏳ Model is loading... This is normal for the first request. Please try again.")
                return None
            else:
                status_desc = response.text[:200] if response.text else "Unknown error"
                print(f"❌ Error {response.status_code}: {status_desc}")
                return None
                
        except requests.Timeout:
            print("❌ Request timed out. Model may still be loading.")
            return None
        except Exception as e:
            print(f"❌ Error calling API: {str(e)}")
            return None
    
    def transform_room(self, image_path, client_data, theme_info):
        """
        Transform room using FLUX.2-klein-9B via HuggingFace Inference API
        
        Args:
            image_path: path to reference image (used for context)
            client_data: dict with client preferences
            theme_info: dict with theme details
        
        Returns:
            dict with transformation result
        """
        try:
            # Load reference image (for context only)
            if isinstance(image_path, str):
                ref_image = Image.open(image_path).convert("RGB")
            else:
                ref_image = image_path.convert("RGB")
            
            # Build detailed prompt
            full_prompt = self.build_detailed_prompt(client_data, theme_info)
            
            # Call API
            result_image = self._call_text_to_image_api(full_prompt)
            
            if result_image is None:
                raise Exception("Failed to generate image. Model may be loading or rate limit reached. Please try again.")
            
            print(f"✅ Generation successful!")
            
            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = client_data.get('name', 'client').replace(' ', '_')
            image_filename = f"{client_name}_{timestamp}_flux_transformed.png"
            image_path = self.output_dir / image_filename
            result_image.save(image_path)
            
            print(f"💾 Saved to: {image_path}")
            
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
                "model": "FLUX.2-klein-9B (HuggingFace Inference API)"
            }
            
        except Exception as e:
            print(f"❌ Error in transform_room: {str(e)}")
            raise
