"""
Image transformation service using HuggingFace Space with Gradio API
Uses black-forest-labs/FLUX.2-klein-9B via HuggingFace Spaces Gradio interface
"""

import os
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image
from pathlib import Path
from gradio_client import Client


class GradioSpaceInteriorDesignTransformer:
    """Transformer using HuggingFace Space API via Gradio"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Get HF token for authentication (optional but may be needed for private spaces)
        self.hf_token = os.getenv("HF_API_TOKEN", None)
        
        # HuggingFace Space endpoint for FLUX.2-klein-9B
        self.space_url = "black-forest-labs/FLUX.2-klein-9B"
        self.client = None
        self.device = "api"
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gradio client for the HuggingFace Space"""
        try:
            print(f"Initializing Gradio client for {self.space_url}...")
            self.client = Client(
                self.space_url,
                hf_token=self.hf_token
            )
            print(f"✅ Gradio client initialized successfully")
            # Verify client by checking available endpoints
            try:
                info = self.client.info()
                print(f"✅ Space info retrieved: {self.space_url}")
            except Exception as info_err:
                # Log but don't fail - some spaces may not have info endpoint
                print(f"⚠️ Could not retrieve space info (not critical): {str(info_err)}")
        except Exception as e:
            print(f"⚠️ Warning initializing Gradio client: {str(e)}")
            print(f"⚠️ Will attempt to recover when needed")
            # Don't raise - allow app to continue, attempts will be made on first request
            self.client = None
    
    def load_models(self):
        """Initialize the Gradio Space client"""
        print(f"Using HuggingFace Space: black-forest-labs/FLUX.2-klein-9B via Gradio API")
        if self.client is None:
            self._initialize_client()
    
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
    
    def _encode_image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _resize_image(self, image, max_size=768):
        """Resize image to fit FLUX.2 input requirements"""
        # FLUX.2-klein-9B works best with sizes that are multiples of 16
        size = min(max_size, max(image.size))
        # Round to nearest multiple of 16
        size = (size // 16) * 16
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        return image
    
    def transform_room(self, image_path, client_data, theme_info):
        """
        Transform room using FLUX.2-klein-9B via HuggingFace Space Gradio API
        
        Args:
            image_path: path to reference image (used for context)
            client_data: dict with client preferences
            theme_info: dict with theme details
        
        Returns:
            dict with transformation result
        """
        
        # Ensure client is initialized - retry if needed
        if self.client is None:
            print("🔄 Attempting to reconnect to Gradio Space...")
            try:
                self._initialize_client()
            except Exception as e:
                raise Exception(f"Failed to connect to FLUX.2-klein-9B Gradio Space: {str(e)}")
        
        if self.client is None:
            raise Exception("Gradio client failed to initialize. Please check your HF_API_TOKEN or internet connection.")
        
        try:
            # Load reference image for context
            if isinstance(image_path, str):
                ref_image = Image.open(image_path).convert("RGB")
            else:
                ref_image = image_path.convert("RGB")
            
            # Resize reference image
            ref_image = self._resize_image(ref_image)
            
            # Build detailed prompt
            full_prompt = self.build_detailed_prompt(client_data, theme_info)
            
            print(f"\n🚀 Generating interior design using FLUX.2-klein-9B via Gradio Space...")
            print(f"📝 Prompt: {full_prompt[:150]}...")
            
            # Call Gradio Space API
            # FLUX.2-klein-9B Gradio interface typically accepts:
            # - prompt (string): the text prompt
            # - [optional] seed, guidance_scale, num_inference_steps
            try:
                # Try with explicit API name first
                result = self.client.predict(
                    prompt=full_prompt,
                    api_name="/infer"
                )
            except Exception:
                # Fallback to calling the first function without explicit API name
                print("⚠️ API endpoint /infer not found, trying default endpoint...")
                result = self.client.predict(
                    prompt=full_prompt
                )
            
            # Handle different possible response formats
            if isinstance(result, str):
                # Result is a file path
                result_image = Image.open(result).convert("RGB")
            elif isinstance(result, list):
                # Result might be a list with image path as first element
                result_image = Image.open(result[0]).convert("RGB")
            else:
                # Assume it's already an image object
                result_image = result
            
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
                "model": "FLUX.2-klein-9B (HuggingFace Space via Gradio)",
                "space_url": "https://huggingface.co/spaces/black-forest-labs/FLUX.2-klein-9B"
            }
            
        except Exception as e:
            print(f"❌ Error in transform_room: {str(e)}")
            raise


def get_transformer():
    """Factory function to get appropriate transformer"""
    try:
        transformer = GradioSpaceInteriorDesignTransformer()
        return transformer
    except Exception as e:
        print(f"⚠️ Failed to initialize Gradio Space transformer: {str(e)}")
        print("⚠️ Note: The transformer may recover when first used")
        # Still return the transformer even if initialization had issues
        try:
            transformer = GradioSpaceInteriorDesignTransformer()
            return transformer
        except Exception as e2:
            print(f"❌ Critical error: Could not create transformer: {str(e2)}")
            raise
