"""
Image Transformation Service for Interior Design
Uses HuggingFace models for room transformation
"""

import os
import base64
import json
from io import BytesIO
from datetime import datetime
from PIL import Image
import torch
from pathlib import Path

# HuggingFace imports
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers import StableDiffusionXLPipeline
import numpy as np
from transformers import DPTImageProcessor, DPTForDepthEstimation

# Check GPU availability
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")


class InteriorDesignTransformer:
    """Main class for room image transformation"""
    
    def __init__(self):
        self.device = DEVICE
        self.prompt_history_dir = Path("prompt_history")
        self.output_dir = Path("generated_images")
        self.prompt_history_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize models (lazy loading)
        self.depth_processor = None
        self.depth_model = None
        self.pipeline = None
        self.controlnet = None
        
    def load_models(self):
        """Load HuggingFace models"""
        print("Loading models...")
        
        # Load depth estimation model for ControlNet
        print("Loading depth estimation model...")
        self.depth_processor = DPTImageProcessor.from_pretrained("Intel/dpt-hybrid-midas")
        self.depth_model = DPTForDepthEstimation.from_pretrained(
            "Intel/dpt-hybrid-midas", 
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)
        
        # Load ControlNet with depth
        print("Loading ControlNet model...")
        self.controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-depth",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        
        # Load main pipeline (Instruct-Pix2Pix or SDXL with ControlNet)
        print("Loading diffusion pipeline...")
        self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=self.controlnet,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)
        
        self.pipeline.scheduler = UniPCMultistepScheduler.from_config(
            self.pipeline.scheduler.config
        )
        
        print("Models loaded successfully!")
    
    def extract_depth_map(self, image):
        """Extract depth map from image using ControlNet"""
        print("Extracting depth map...")
        
        # Prepare image
        inputs = self.depth_processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.depth_model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        # Interpolate to original size
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image.size[::-1],
            mode="bicubic",
            align_corners=False,
        )
        
        # Convert to numpy and normalize
        output = prediction.squeeze().cpu().numpy()
        depth = (output * 255 / np.max(output)).astype("uint8")
        
        # Convert to PIL Image
        depth_image = Image.fromarray(depth)
        return depth_image
    
    def build_detailed_prompt(self, client_data, theme_info):
        """Build detailed transformation prompt"""
        
        prompt = f"""
Transform this room into a {theme_info.get('theme_name', 'Modern')} interior.

STYLE:
{theme_info.get('style_description', 'Contemporary and functional')}

COLOR PALETTE:
{theme_info.get('color_palette', 'Warm neutrals and accent colors')}

MOOD:
Cozy, organized, welcoming, {theme_info.get('mood', 'comfortable')}

DESIGN ELEMENTS:
{theme_info.get('design_elements', 'Minimalist furniture, plants, natural textures')}

RULES:
- Preserve room architecture and layout
- Maintain realistic furniture scale
- Declutter space, organized storage solutions
- Warm interior lighting
- Natural materials and textures where appropriate
- Accessible and functional layout

PERSONALIZATION:
Hobbies & Interests: {client_data.get('hobbies', '')}
Space Requirements: {client_data.get('requirements', '')}
Client Preferences: {client_data.get('likes', '')}
Avoid: {client_data.get('dislikes', '')}

QUALITY SPECIFICATIONS:
- Architectural visualization quality
- Professional interior design photography
- Realistic perspective and proportions
- Coherent lighting and shadows
- High resolution details
"""
        return prompt.strip()
    
    def save_prompt_history(self, client_name, prompt, image_filename, theme):
        """Save prompt history to file"""
        timestamp = datetime.now().isoformat()
        prompt_file = self.prompt_history_dir / f"{client_name}_{timestamp.split('T')[0]}_prompt.txt"
        
        content = f"""
CLIENT DESIGN TRANSFORMATION PROMPT
Generated: {timestamp}
Theme: {theme}

{'='*60}

{prompt}

{'='*60}
Generated Image: {image_filename}
"""
        
        with open(prompt_file, 'w') as f:
            f.write(content)
        
        print(f"Prompt saved to: {prompt_file}")
        return str(prompt_file)
    
    def transform_room(self, image, client_data, theme_info):
        """
        Main transformation function
        
        Args:
            image: PIL Image or image path
            client_data: dict with client preferences
            theme_info: dict with theme details
            
        Returns:
            dict with generated image and metadata
        """
        
        # Load models if not already loaded
        if self.pipeline is None:
            self.load_models()
        
        # Load image if path provided
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        
        # Ensure correct size
        width, height = image.size
        image = image.resize((768, 576))  # Adjust to multiple of 64
        
        # Build detailed prompt
        full_prompt = self.build_detailed_prompt(client_data, theme_info)
        
        # Extract depth map for ControlNet
        depth_map = self.extract_depth_map(image)
        depth_map = depth_map.resize((768, 576))
        
        # Create transformation prompt
        transformation_prompt = f"""
Transform this room into: {full_prompt}

preserve room layout,
correct perspective,
realistic interior photography,
organized clutter-free space,
professional quality
"""
        
        print(f"Transformation Prompt:\n{transformation_prompt}")
        
        # Generate image with ControlNet
        print("Generating transformed image...")
        with torch.autocast(self.device):
            result = self.pipeline(
                prompt=transformation_prompt,
                image=image,
                control_image=depth_map,
                height=576,
                width=768,
                num_inference_steps=30,
                guidance_scale=7.5,
                controlnet_conditioning_scale=1.0,
                negative_prompt="blurry, distorted, ugly, bad quality, weird perspective"
            ).images[0]
        
        # Save generated image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = client_data.get('name', 'client').replace(' ', '_')
        image_filename = f"{client_name}_{timestamp}_transformed.png"
        image_path = self.output_dir / image_filename
        result.save(image_path)
        
        print(f"Generated image saved to: {image_path}")
        
        # Save prompt history
        prompt_file = self.save_prompt_history(
            client_name, 
            full_prompt,
            image_filename,
            theme_info.get('theme_name', 'Custom')
        )
        
        # Convert to base64 for frontend
        buffered = BytesIO()
        result.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "status": "success",
            "image_base64": img_base64,
            "image_path": str(image_path),
            "prompt_history": prompt_file,
            "theme": theme_info.get('theme_name'),
            "timestamp": timestamp
        }


# Initialize transformer
transformer = InteriorDesignTransformer()


def create_theme_from_design_brief(brief_prompt):
    """
    Parse the design brief and create theme information
    
    Args:
        brief_prompt: Generated design brief from form
        
    Returns:
        dict with theme information
    """
    
    return {
        "theme_name": "Personalized",
        "style_description": "Based on client preferences and aesthetic",
        "color_palette": "Client selected colors",
        "mood": "Tailored to lifestyle",
        "design_elements": "Customized based on likes and interests",
        "brief": brief_prompt
    }


if __name__ == "__main__":
    print("Interior Design Image Transformation Service")
    print("Ready for API integration")
