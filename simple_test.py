#!/usr/bin/env python3
"""
Simple test script for the First Frame Extractor FastAPI application.

This is a lightweight version for quick testing.
"""

import requests
import os


def test_api():
    """Simple test function."""
    base_url = "http://localhost:8000"
    
    print("🚀 Simple Test for First Frame Extractor API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Server is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server!")
        print("   Make sure to start the server first:")
        print("   python main.py")
        return
    
    print()
    
    # Test 2: Check if you have a video file to test
    video_files = []
    common_video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    print("2. Looking for video files in current directory...")
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in common_video_extensions):
            video_files.append(file)
    
    if video_files:
        print(f"   Found video files: {video_files}")
        test_video = video_files[0]
        print(f"   Using: {test_video}")
    else:
        print("   No video files found in current directory.")
        print("   Please add a video file (.mp4, .avi, .mov, etc.) to test with")
        print("   Or run the comprehensive test: python test_app.py")
        return
    
    print()
    
    # Test 3: Extract first frame
    print("3. Testing first frame extraction...")
    try:
        with open(test_video, 'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(f"{base_url}/extract-first-frame/", files=files)
        
        if response.status_code == 200:
            output_file = f"first_frame_{os.path.splitext(test_video)[0]}.jpg"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"   ✅ First frame extracted successfully!")
            print(f"   Saved as: {output_file}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"   ❌ Extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Extract first frame with info
    print("4. Testing first frame extraction with video info...")
    try:
        with open(test_video, 'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(f"{base_url}/extract-first-frame-info/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            video_info = data.get('video_info', {})
            print(f"   ✅ Extraction with info successful!")
            print(f"   Video dimensions: {video_info.get('width')}x{video_info.get('height')}")
            print(f"   FPS: {video_info.get('fps')}")
            print(f"   Duration: {video_info.get('duration_seconds'):.2f} seconds")
        else:
            print(f"   ❌ Extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("🎉 Simple test completed!")
    print("For comprehensive testing, run: python test_app.py")


if __name__ == "__main__":
    test_api()
