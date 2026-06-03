#!/usr/bin/env python3
"""
Custom test script for testing with your specific video file.
"""

import requests
import os
import time

def test_with_custom_video(video_path):
    """Test the API with your specific video file."""
    base_url = "http://localhost:8088"
    
    print(f"🎬 Testing with your video: {video_path}")
    print("=" * 60)
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        print("Please provide the correct path to your video file.")
        return
    
    # Check server
    print("1. Checking server...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Server is running!")
        else:
            print(f"   ❌ Server error: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server!")
        print("   Start server with: python main.py")
        return
    
    print()
    
    # Test 1: Extract first frame as image
    print("2. Extracting first frame as image...")
    try:
        with open(video_path, 'rb') as video_file:
            files = {'file': (os.path.basename(video_path), video_file)}
            start_time = time.time()
            response = requests.post(f"{base_url}/extract-first-frame/", files=files)
            end_time = time.time()
        
        if response.status_code == 200:
            # Save the image
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"first_frame_{video_name}.jpg"
            
            with open(output_path, 'wb') as output_file:
                output_file.write(response.content)
            
            print(f"   ✅ Success! Processing time: {end_time - start_time:.3f} seconds")
            print(f"   📁 First frame saved as: {output_path}")
            print(f"   📊 Image size: {len(response.content):,} bytes")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print()
    
    # Test 2: Extract first frame with video info
    print("3. Extracting first frame with video info...")
    try:
        with open(video_path, 'rb') as video_file:
            files = {'file': (os.path.basename(video_path), video_file)}
            start_time = time.time()
            response = requests.post(f"{base_url}/extract-first-frame-info/", files=files)
            end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            video_info = data.get('video_info', {})
            
            print(f"   ✅ Success! Processing time: {end_time - start_time:.3f} seconds")
            print(f"   📹 Video Information:")
            print(f"      • Filename: {video_info.get('filename')}")
            print(f"      • Dimensions: {video_info.get('width')}x{video_info.get('height')}")
            print(f"      • FPS: {video_info.get('fps'):.2f}")
            print(f"      • Frame Count: {video_info.get('frame_count')}")
            print(f"      • Duration: {video_info.get('duration_seconds'):.2f} seconds")
            print(f"      • File Size: {video_info.get('file_size_bytes'):,} bytes")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("🎉 Custom video test completed!")


if __name__ == "__main__":
    # CHANGE THIS PATH TO YOUR VIDEO FILE
    video_path = input("Enter the path to your video file: ").strip()
    
    # Remove quotes if user added them
    video_path = video_path.strip('"').strip("'")
    
    test_with_custom_video(video_path)
