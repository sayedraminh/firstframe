#!/usr/bin/env python3
"""
Test script for the First Frame Extractor FastAPI application.

This script provides comprehensive testing for the video first frame extraction API,
including unit tests and integration tests with sample videos.
"""

import requests
import json
import base64
import os
import tempfile
import cv2
import numpy as np
from pathlib import Path
import time


class FirstFrameExtractorTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def create_test_video(self, filename, duration_seconds=2, fps=30, width=640, height=480):
        """Create a simple test video for testing purposes."""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        total_frames = int(duration_seconds * fps)
        
        for frame_num in range(total_frames):
            # Create a frame with different colors and frame number
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Different color for each frame
            color_intensity = int((frame_num / total_frames) * 255)
            frame[:, :] = [color_intensity, 100, 255 - color_intensity]
            
            # Add frame number text
            cv2.putText(frame, f"Frame {frame_num}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        return filename
    
    def test_health_check(self):
        """Test the health check endpoint."""
        print("🔍 Testing health check endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure the FastAPI server is running!")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_extract_first_frame_image(self, video_path):
        """Test the extract first frame endpoint (returns image)."""
        print(f"🔍 Testing first frame extraction (image) with {video_path}...")
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'file': video_file}
                start_time = time.time()
                response = requests.post(f"{self.base_url}/extract-first-frame/", files=files)
                end_time = time.time()
                
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                # Save the extracted frame
                output_path = f"extracted_frame_{Path(video_path).stem}.jpg"
                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)
                
                print(f"✅ First frame extracted successfully")
                print(f"   Processing time: {processing_time:.3f} seconds")
                print(f"   Output saved to: {output_path}")
                print(f"   Image size: {len(response.content)} bytes")
                print(f"   Content type: {response.headers.get('content-type')}")
                return True
            else:
                print(f"❌ First frame extraction failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ First frame extraction error: {e}")
            return False
    
    def test_extract_first_frame_with_info(self, video_path):
        """Test the extract first frame with info endpoint (returns JSON)."""
        print(f"🔍 Testing first frame extraction with info for {video_path}...")
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'file': video_file}
                start_time = time.time()
                response = requests.post(f"{self.base_url}/extract-first-frame-info/", files=files)
                end_time = time.time()
                
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                video_info = data.get('video_info', {})
                
                print(f"✅ First frame with info extracted successfully")
                print(f"   Processing time: {processing_time:.3f} seconds")
                print(f"   Video info:")
                print(f"     - Filename: {video_info.get('filename')}")
                print(f"     - Dimensions: {video_info.get('width')}x{video_info.get('height')}")
                print(f"     - FPS: {video_info.get('fps')}")
                print(f"     - Frame count: {video_info.get('frame_count')}")
                print(f"     - Duration: {video_info.get('duration_seconds'):.2f} seconds")
                print(f"     - File size: {video_info.get('file_size_bytes')} bytes")
                
                # Optionally save the base64 image
                if 'image_base64' in data:
                    image_data = base64.b64decode(data['image_base64'])
                    output_path = f"extracted_frame_info_{Path(video_path).stem}.jpg"
                    with open(output_path, 'wb') as output_file:
                        output_file.write(image_data)
                    print(f"   Frame saved to: {output_path}")
                
                return True
            else:
                print(f"❌ First frame with info extraction failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ First frame with info extraction error: {e}")
            return False
    
    def test_invalid_file(self):
        """Test with an invalid file (not a video)."""
        print("🔍 Testing with invalid file...")
        
        try:
            # Create a dummy text file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write("This is not a video file")
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as test_file:
                    files = {'file': test_file}
                    response = requests.post(f"{self.base_url}/extract-first-frame/", files=files)
                
                if response.status_code == 400:
                    print("✅ Invalid file correctly rejected")
                    print(f"   Error message: {response.json()}")
                    return True
                else:
                    print(f"❌ Invalid file test failed: Expected 400, got {response.status_code}")
                    return False
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"❌ Invalid file test error: {e}")
            return False
    
    def test_no_file(self):
        """Test with no file uploaded."""
        print("🔍 Testing with no file...")
        
        try:
            response = requests.post(f"{self.base_url}/extract-first-frame/")
            
            if response.status_code == 422:  # Unprocessable Entity
                print("✅ No file correctly rejected")
                print(f"   Error message: {response.json()}")
                return True
            else:
                print(f"❌ No file test failed: Expected 422, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ No file test error: {e}")
            return False
    
    def performance_test(self, video_path, num_requests=5):
        """Test performance with multiple requests."""
        print(f"🔍 Performance testing with {num_requests} requests...")
        
        times = []
        successful_requests = 0
        
        for i in range(num_requests):
            try:
                with open(video_path, 'rb') as video_file:
                    files = {'file': video_file}
                    start_time = time.time()
                    response = requests.post(f"{self.base_url}/extract-first-frame/", files=files)
                    end_time = time.time()
                    
                if response.status_code == 200:
                    times.append(end_time - start_time)
                    successful_requests += 1
                    print(f"   Request {i+1}/{num_requests}: {end_time - start_time:.3f}s")
                else:
                    print(f"   Request {i+1}/{num_requests}: Failed ({response.status_code})")
                    
            except Exception as e:
                print(f"   Request {i+1}/{num_requests}: Error - {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"✅ Performance test completed")
            print(f"   Successful requests: {successful_requests}/{num_requests}")
            print(f"   Average time: {avg_time:.3f}s")
            print(f"   Min time: {min_time:.3f}s")
            print(f"   Max time: {max_time:.3f}s")
            return True
        else:
            print("❌ Performance test failed - no successful requests")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting comprehensive tests for First Frame Extractor API")
        print("=" * 60)
        
        # Check if server is running
        if not self.test_health_check():
            print("\n❌ Server is not running. Please start the FastAPI server first:")
            print("   python main.py")
            print("   or")
            print("   uvicorn main:app --host 0.0.0.0 --port 8000")
            return
        
        print("\n" + "=" * 60)
        
        # Create test videos
        print("📹 Creating test videos...")
        test_videos = []
        
        # Create a small test video
        small_video = "test_video_small.mp4"
        self.create_test_video(small_video, duration_seconds=1, fps=10, width=320, height=240)
        test_videos.append(small_video)
        print(f"   Created: {small_video}")
        
        # Create a larger test video
        large_video = "test_video_large.mp4"
        self.create_test_video(large_video, duration_seconds=3, fps=30, width=1280, height=720)
        test_videos.append(large_video)
        print(f"   Created: {large_video}")
        
        print("\n" + "=" * 60)
        
        # Run tests
        test_results = []
        
        # Test both endpoints with both videos
        for video in test_videos:
            test_results.append(self.test_extract_first_frame_image(video))
            print()
            test_results.append(self.test_extract_first_frame_with_info(video))
            print()
        
        # Error handling tests
        test_results.append(self.test_invalid_file())
        print()
        test_results.append(self.test_no_file())
        print()
        
        # Performance test with small video
        test_results.append(self.performance_test(test_videos[0], num_requests=3))
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Your FastAPI application is working perfectly!")
        else:
            print(f"\n⚠️  Some tests failed. Please check the error messages above.")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test files...")
        for video in test_videos:
            if os.path.exists(video):
                os.remove(video)
                print(f"   Removed: {video}")


def main():
    """Main function to run tests."""
    print("First Frame Extractor API Tester")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print()
    
    # You can change the base URL if your server is running on a different port
    tester = FirstFrameExtractorTester(base_url="http://localhost:8000")
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")


if __name__ == "__main__":
    main()
