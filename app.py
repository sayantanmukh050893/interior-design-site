"""
Flask API Server for Interior Design Image Transformation
Provides endpoints for room transformation with AI
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from image_service_hf_api import get_transformer
import json
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Initialize transformer (uses Hugging Face API or mock based on HF_API_TOKEN)
transformer = get_transformer()

# Flask app setup
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
REQUEST_TIMEOUT = 600  # 10 minutes for transformation

UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    static_files = ['styles.css', 'script.js', 'styles.css.map', 'script.js.map']
    if filename in static_files or filename.startswith(('generated_images/', 'uploads/')):
        return send_from_directory('.', filename)
    # If file not found in static files, return 404
    return jsonify({"status": "error", "message": "File not found"}), 404


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Interior Design Image Transformation",
        "gpu_available": "cuda" in transformer.device
    })


@app.route('/load-models', methods=['POST'])
def load_models_endpoint():
    """Load HuggingFace models"""
    try:
        logger.info("Loading models...")
        transformer.load_models()
        return jsonify({
            "status": "success",
            "message": "Models loaded successfully"
        })
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/transform', methods=['POST'])
def transform_image():
    """
    Main transformation endpoint
    
    Expects:
    - image: Image file
    - client_data: JSON with client information
    - theme_info: JSON with theme details
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error",
                "message": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Get form data
        client_data_str = request.form.get('client_data', '{}')
        theme_info_str = request.form.get('theme_info', '{}')
        
        try:
            client_data = json.loads(client_data_str)
            theme_info = json.loads(theme_info_str)
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON in client_data or theme_info"
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = UPLOAD_FOLDER / filename
        file.save(str(temp_path))
        
        logger.info(f"Processing image: {filename}")
        
        # Transform image
        result = transformer.transform_room(str(temp_path), client_data, theme_info)
        
        # Clean up temp file
        temp_path.unlink()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error transforming image: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    """
    Generate detailed design prompt from client data
    
    Expects JSON:
    - client_name
    - preferred_colors
    - likes
    - dislikes
    - hobbies
    - requirements
    - additional_comments
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Create theme from design brief
        brief_prompt = f"""
Colors: {data.get('preferred_colors', '')}
Likes: {data.get('likes', '')}
Dislikes: {data.get('dislikes', '')}
Hobbies: {data.get('hobbies', '')}
Requirements: {data.get('requirements', '')}
"""
        
        theme_info = {
            "theme_name": "Personalized Design",
            "style_description": f"Based on preference for {data.get('likes', 'modern style')}",
            "color_palette": data.get('preferred_colors', 'Neutral tones'),
            "mood": "Comfortable, welcoming, and functional",
            "design_elements": f"Incorporating hobbies: {data.get('hobbies', 'reading, relaxation')}"
        }
        
        # Build full prompt
        full_prompt = transformer.build_detailed_prompt(data, theme_info)
        
        return jsonify({
            "status": "success",
            "prompt": full_prompt,
            "theme_info": theme_info
        })
        
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/prompt-history/<client_name>', methods=['GET'])
def get_prompt_history(client_name):
    """Retrieve prompt history for a client"""
    try:
        history_files = list(Path("prompt_history").glob(f"{client_name}*"))
        
        history = []
        for file in history_files:
            with open(file, 'r') as f:
                history.append({
                    "filename": file.name,
                    "content": f.read()
                })
        
        return jsonify({
            "status": "success",
            "client": client_name,
            "history_count": len(history),
            "entries": history
        })
        
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/generated-images/<filename>', methods=['GET'])
def get_generated_image(filename):
    """Retrieve generated image"""
    try:
        image_path = Path("generated_images") / secure_filename(filename)
        
        if not image_path.exists():
            return jsonify({
                "status": "error",
                "message": "Image not found"
            }), 404
        
        return send_file(
            str(image_path),
            mimetype='image/png',
            as_attachment=False,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        "status": "error",
        "message": f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


if __name__ == '__main__':
    logger.info("Starting Interior Design Image Transformation API Server")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Max file size: {MAX_FILE_SIZE / (1024*1024)}MB")
    
    # Note: For production, use gunicorn or similar WSGI server
    # Example: gunicorn -w 1 -b 0.0.0.0:5001 app:app --timeout 300
    app.run(debug=False, host='0.0.0.0', port=5001, threaded=False)
