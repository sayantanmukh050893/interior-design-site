"""
Image transformation service using multiple fallback strategies
Tries: HF Router API → Gradio Direct Call → Mock for testing
"""

import os
import base64
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image
from pathlib import Path
import json


class FLUXTransformer:
    """Flexible FLUX transformer with multiple strategies"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Get API token
        self.api_token = os.getenv("HF_API_TOKEN", None)
        self.model_id = "black-forest-labs/FLUX.2-klein-9B"
        
        # HuggingFace endpoints
        self.hf_router_url = f"https://router.huggingface.co/models/{self.model_id}"
        self.hf_inference_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        
        # HuggingFace Space endpoint
        self.space_url = "https://black-forest-labs-flux-2-klein-9b.hf.space"
        self.space_api_url = f"{self.space_url}/api/predict"
        
        self.device = "api"
        self.strategy_used = None
        
        if not self.api_token:
            print("⚠️  Warning: HF_API_TOKEN not set")
            print("   Falling back to HuggingFace Space (Gradio)")
            print("   For better performance, set: export HF_API_TOKEN='your_token'")
    
    def load_models(self):
        """Initialize models"""
        print(f"Using FLUX.2-klein-9B via HuggingFace")
    
    def build_detailed_prompt(self, client_data, theme_info):
        """Build prompt for FLUX"""
        prompt = f"""Professional interior design photograph of a {theme_info.get('theme_name', 'Modern')} {client_data.get('room_type', 'living room')}.

DESIGN STYLE: {theme_info.get('style_description', 'Contemporary')}
COLOR PALETTE: {theme_info.get('color_palette', 'Neutral tones')}

KEY DESIGN FEATURES:
- {client_data.get('likes', 'Well-organized layout')}
- Natural and ambient lighting
- Premium furniture and decoration
- Professional interior styling
- Photorealistic, magazine-quality photography
- High-resolution, sharp details"""
        
        return prompt.strip()
    
    def save_prompt_history(self, client_name, prompt, image_filename, theme):
        """Save prompt to file"""
        timestamp = datetime.now().isoformat()
        prompt_file = self.prompt_history_dir / f"{client_name}_{timestamp.split('T')[0]}_prompt.txt"
        
        content = f"""CLIENT DESIGN TRANSFORMATION PROMPT
Generated: {timestamp}
Theme: {theme}
Strategy: {self.strategy_used}

{prompt}

Generated Image: {image_filename}
"""
        
        with open(prompt_file, 'w') as f:
            f.write(content)
        
        return str(prompt_file)
    
    def _encode_image_to_base64(self, image):
        """Convert PIL Image to base64"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _try_hf_router_api(self, prompt):
        """Try HuggingFace router API (requires token)"""
        if not self.api_token:
            return None
        
        try:
            print(f"🔄 Trying HuggingFace Router API...")
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {"inputs": prompt}
            
            response = requests.post(
                self.hf_router_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                print("✅ HuggingFace Router API successful")
                return Image.open(BytesIO(response.content))
            else:
                print(f"⏭️ Router API failed ({response.status_code}), trying next strategy...")
                return None
                
        except Exception as e:
            print(f"⏭️ Router API error: {str(e)}")
            return None
    
    def _try_inference_api(self, prompt):
        """Try direct inference API"""
        try:
            print(f"🔄 Trying HuggingFace Inference API...")
            
            headers = {"Content-Type": "application/json"}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            payload = {"inputs": prompt}
            
            response = requests.post(
                self.hf_inference_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                print("✅ Inference API successful")
                return Image.open(BytesIO(response.content))
            elif response.status_code == 410:
                print(f"⏭️ Inference API deprecated (410), trying next strategy...")
                return None
            else:
                print(f"⏭️ Inference API failed ({response.status_code}), trying next strategy...")
                return None
                
        except Exception as e:
            print(f"⏭️ Inference API error: {str(e)}")
            return None
    
    def _try_gradio_space_direct(self, prompt):
        """Try calling Gradio Space directly via API"""
        try:
            print(f"🔄 Trying HuggingFace Space Gradio API...")
            
            # Try predicting with the prompt
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            # Gradio expects JSON with the input
            data = json.dumps({"data": [prompt]})
            headers["Content-Type"] = "application/json"
            
            response = requests.post(
                self.space_api_url,
                headers=headers,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                # Gradio returns data array with image path or base64
                if "data" in result and len(result["data"]) > 0:
                    image_data = result["data"][0]
                    if isinstance(image_data, str):
                        # Try to load from URL or base64
                        if image_data.startswith("http"):
                            # It's a URL, download it
                            img_response = requests.get(image_data, timeout=30)
                            if img_response.status_code == 200:
                                return Image.open(BytesIO(img_response.content))
                        elif image_data.startswith("data:"):
                            # It's base64
                            base64_str = image_data.split(",")[1]
                            return Image.open(BytesIO(base64.b64decode(base64_str)))
                        else:
                            # Try as file path
                            try:
                                return Image.open(image_data)
                            except:
                                pass
            
            print(f"⏭️ Gradio Space API response format unexpected, trying next...")
            return None
                
        except Exception as e:
            print(f"⏭️ Gradio Space error: {str(e)}")
            return None
    
    def _generate_test_image(self):
        """Generate a test image as fallback (for demonstration)"""
        print(f"🎨 Generating demonstration image...")
        # Create a stylized version of the input
        img = Image.new('RGB', (512, 768), color=(220, 200, 180))
        return img
    
    def transform_room(self, image_path, client_data, theme_info):
        """Transform room - tries multiple strategies"""
        try:
            # Load reference image
            if isinstance(image_path, str):
                ref_image = Image.open(image_path).convert("RGB")
            else:
                ref_image = image_path.convert("RGB")
            
            # Build prompt
            full_prompt = self.build_detailed_prompt(client_data, theme_info)
            
            # Try strategies in order
            result_image = None
            strategies = [
                ("HuggingFace Router API", self._try_hf_router_api),
                ("HuggingFace Inference API", self._try_inference_api),
                ("HuggingFace Space Gradio", self._try_gradio_space_direct),
            ]
            
            for strategy_name, strategy_func in strategies:
                result_image = strategy_func(full_prompt)
                if result_image is not None:
                    self.strategy_used = strategy_name
                    print(f"✅ Using strategy: {strategy_name}")
                    break
            
            # If all fail, use test image
            if result_image is None:
                print(f"\n⚠️ All API strategies failed")
                print(f"   HF_API_TOKEN set: {'Yes' if self.api_token else 'No'}")
                print(f"   HuggingFace APIs may need a valid token")
                print(f"   Or the service may be temporarily unavailable")
                raise Exception(
                    "Failed to generate image. Please:"
                    "\n1. Set HF_API_TOKEN environment variable"
                    "\n2. Wait a moment and try again"
                    "\n3. Check HuggingFace status"
                )
            
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
                "model": f"FLUX.2-klein-9B ({self.strategy_used})"
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
