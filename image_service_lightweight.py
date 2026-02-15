"""
Alternative lighter-weight image transformation service
For CPU-only or low-VRAM systems
"""

import os
import base64
import json
from io import BytesIO
from datetime import datetime
from PIL import Image
from pathlib import Path

# For lightweight systems, use InstrutPixel2Pix instead of full ControlNet
try:
    from diffusers import StableDiffusionInstructPix2PixPipeline
    INSTRUCT_PIX2PIX_AVAILABLE = True
except ImportError:
    INSTRUCT_PIX2PIX_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class LightweightInteriorDesignTransformer:
    """Lightweight transformer for systems without GPU"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        self.pipeline = None
        self.device = "cpu"
        
        if TORCH_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_models(self):
        """Load lightweight models"""
        print(f"Loading models on {self.device}...")
        
        if not INSTRUCT_PIX2PIX_AVAILABLE:
            raise ImportError("diffusers library required: pip install diffusers")
        
        # Use Instruct-Pix2Pix - smaller, faster, no ControlNet needed
        model_id = "timbrooks/instruct-pix2pix"
        
        self.pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
        ).to(self.device)
        
        if self.device == "cpu":
            # Enable memory optimization for CPU
            self.pipeline.enable_attention_slicing()
        
        print("Lightweight model loaded!")
    
    def build_detailed_prompt(self, client_data, theme_info):
        """Build transformation prompt"""
        
        prompt = f"""
Transform this room into a {theme_info.get('theme_name', 'Modern')} interior.

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
- Professional quality
"""
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
    
    def transform_room(self, image, client_data, theme_info):
        """
        Lightweight image transformation
        
        Args:
            image: PIL Image or image path
            client_data: dict with client preferences
            theme_info: dict with theme details
        """
        
        if self.pipeline is None:
            self.load_models()
        
        # Load image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        
        # Resize for processing (smaller = faster)
        width, height = image.size
        image = image.resize((512, 384))  # Multiple of 64
        
        # Build prompt
        full_prompt = self.build_detailed_prompt(client_data, theme_info)
        
        print(f"Generating with prompt:\n{full_prompt}")
        
        # Generate - Instruct-Pix2Pix is simpler than full pipeline
        import torch
        with torch.inference_mode():
            result = self.pipeline(
                prompt=full_prompt,
                image=image,
                num_inference_steps=20,  # Lower steps = faster
                guidance_scale=7.5,
                image_guidance_scale=1.5
            ).images[0]
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = client_data.get('name', 'client').replace(' ', '_')
        image_filename = f"{client_name}_{timestamp}_transformed.png"
        image_path = self.output_dir / image_filename
        result.save(image_path)
        
        print(f"Saved to: {image_path}")
        
        # Convert to base64
        buffered = BytesIO()
        result.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
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
            "timestamp": timestamp
        }


# Fallback for absolute minimal systems
class MockTransformer:
    """Mock transformer for testing without models"""
    
    def __init__(self):
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def load_models(self):
        print("Mock transformer - no actual models loaded")
    
    def build_detailed_prompt(self, client_data, theme_info):
        return f"Transform room: {theme_info.get('theme_name')}"
    
    def transform_room(self, image, client_data, theme_info):
        """Return mock transformation"""
        if isinstance(image, str):
            result_image = Image.open(image)
        else:
            result_image = image
        
        # Create a simple transformed version
        result_image = result_image.convert("RGB")
        result_image.thumbnail((512, 384))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = client_data.get('name', 'client').replace(' ', '_')
        image_filename = f"{client_name}_{timestamp}_transformed.png"
        image_path = self.output_dir / image_filename
        result_image.save(image_path)
        
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "status": "success",
            "image_base64": img_base64,
            "image_path": str(image_path),
            "theme": theme_info.get('theme_name'),
            "timestamp": timestamp
        }


# Select appropriate transformer based on available resources
def get_transformer():
    """Get appropriate transformer based on system capabilities"""
    
    if not TORCH_AVAILABLE:
        print("Warning: PyTorch not available. Using mock transformer.")
        return MockTransformer()
    
    # For systems with limited resources
    if INSTRUCT_PIX2PIX_AVAILABLE:
        return LightweightInteriorDesignTransformer()
    
    # Fall back to mock if dependencies missing
    print("Warning: Required dependencies not found. Using mock transformer.")
    return MockTransformer()


if __name__ == "__main__":
    print("Lightweight Interior Design Transformer")
    print("Choose deployment:")
    print("1. Full: Use full_image_service.py")
    print("2. Lightweight: Use image_service_lightweight.py")
