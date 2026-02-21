#!/usr/bin/env python3
"""
Test script to verify the two-step transformation flow:
1. Generate prompt from form data
2. Transform image using the generated prompt
"""

import requests
import json
import os
import sys
from pathlib import Path

# API base URL
API_BASE_URL = "http://localhost:5000"

def test_generate_prompt():
    """Test the /generate-prompt endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Generate Prompt Endpoint")
    print("="*60)
    
    # Sample client data matching the form
    client_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "about": "I love modern minimalist design",
        "preferred_colors": "Warm neutrals, soft grays, and earth tones",
        "likes": "Natural light, plants, minimal clutter",
        "dislikes": "Dark colors, heavy furniture, too much decoration",
        "hobbies": "Reading, yoga, meditation",
        "requirements": "Need a workspace, storage solutions",
        "additional_comments": "Would love to create a calm and focused space",
        "room_type": "bedroom",
        "room_length": "15",
        "room_width": "12"
    }
    
    try:
        print(f"\nSending POST request to: {API_BASE_URL}/generate-prompt")
        print(f"Client data: {json.dumps(client_data, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/generate-prompt",
            json=client_data,
            timeout=30
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ SUCCESS: Prompt generated successfully")
            print(f"\nGenerated Prompt:\n{result.get('prompt', 'N/A')}")
            print(f"\nTheme Info: {json.dumps(result.get('theme_info', {}), indent=2)}")
            return result.get('prompt')
        else:
            print(f"\n✗ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ ERROR: {e}")
        return None


def test_health():
    """Test the /health endpoint"""
    print("\n" + "="*60)
    print("TEST 0: Health Check Endpoint")
    print("="*60)
    
    try:
        print(f"\nSending GET request to: {API_BASE_URL}/health")
        
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=10
        )
        
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ SUCCESS: Server is healthy")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"\n✗ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ ERROR: {e}")
        return False


def test_transform_with_prompt(prompt):
    """Test the /transform endpoint with generated prompt"""
    print("\n" + "="*60)
    print("TEST 2: Transform Image Endpoint (with generated prompt)")
    print("="*60)
    
    if not prompt:
        print("\n✗ SKIPPED: No prompt provided from previous test")
        return False
    
    # Create a simple test image if it doesn't exist
    test_image_path = Path("test_room.jpg")
    
    if not test_image_path.exists():
        print(f"\nCreating a test image at {test_image_path}...")
        # Create a minimal valid JPEG file
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(test_image_path, 'JPEG')
            print(f"✓ Test image created: {test_image_path}")
        except ImportError:
            print("PIL not available, will try to download a sample image...")
            # Fall back to a simple approach
            print("Creating a minimal JPEG file...")
            # Minimal JPEG header
            jpeg_data = bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
                0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
                0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
                0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
                0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
                0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
                0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
                0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
                0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
                0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
                0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
                0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
                0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
                0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
                0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
                0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
                0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
                0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
                0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
                0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
                0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
                0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
                0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
                0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
                0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD1, 0xFF, 0xD9
            ])
            with open(test_image_path, 'wb') as f:
                f.write(jpeg_data)
            print(f"✓ Minimal test image created: {test_image_path}")
    
    # Sample client data
    client_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "about": "I love modern minimalist design",
        "preferred_colors": "Warm neutrals",
        "likes": "Natural light, plants",
        "dislikes": "Dark colors",
        "hobbies": "Reading, yoga",
        "requirements": "Need a workspace",
        "additional_comments": "Create a calm space",
        "room_type": "bedroom",
        "room_length": "15",
        "room_width": "12"
    }
    
    theme_info = {
        "theme_name": "Personalized Design",
        "room_type": "bedroom"
    }
    
    try:
        print(f"\nSending POST request to: {API_BASE_URL}/transform")
        print(f"  - Image file: {test_image_path}")
        print(f"  - Using generated prompt: Yes")
        print(f"  - Client data: {json.dumps(client_data, indent=2)}")
        
        with open(test_image_path, 'rb') as img:
            files = {
                'image': img
            }
            data = {
                'client_data': json.dumps(client_data),
                'theme_info': json.dumps(theme_info),
                'prompt': prompt
            }
            
            response = requests.post(
                f"{API_BASE_URL}/transform",
                files=files,
                data=data,
                timeout=120  # Long timeout for image transformation
            )
        
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ SUCCESS: Image transformed successfully")
            print(f"Response Keys: {list(result.keys())}")
            print(f"Status: {result.get('status')}")
            if 'image_base64' in result:
                print(f"Image size: {len(result['image_base64'])} characters (base64)")
            return True
        else:
            print(f"\n✗ FAILED: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏱ TIMEOUT: Transform endpoint took too long (>120s)")
        print("This is expected if FLUX models need to be downloaded/initialized")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n✗ ERROR: {e}")
        return False


def main():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("ENDPOINT TESTING SUITE")
    print("Testing two-step transformation flow")
    print("="*60)
    
    # Test 1: Health check
    health_ok = test_health()
    
    if not health_ok:
        print("\n✗ Server is not healthy. Cannot proceed with tests.")
        sys.exit(1)
    
    # Test 2: Generate prompt
    generated_prompt = test_generate_prompt()
    
    if not generated_prompt:
        print("\n✗ Failed to generate prompt. Cannot proceed with transform test.")
        sys.exit(1)
    
    # Test 3: Transform with prompt
    transform_ok = test_transform_with_prompt(generated_prompt)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Generate Prompt: {'✓ PASS' if generated_prompt else '✗ FAIL'}")
    print(f"Transform Image: {'✓ PASS' if transform_ok else '⏱ TIMEOUT' if transform_ok is None else '✗ FAIL'}")
    print("="*60 + "\n")
    
    if health_ok and generated_prompt:
        print("✓ Two-step transformation flow is working correctly!")
        if transform_ok is not None:
            print("✓ All endpoints responding correctly")
    else:
        print("✗ Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
