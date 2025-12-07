from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
import tempfile
import os
from typing import Optional

app = FastAPI(
    title="First Frame Extractor",
    description="FastAPI app that extracts the first frame from uploaded videos",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "First Frame Extractor API is running"}

@app.post("/extract-first-frame/")
async def extract_first_frame(file: UploadFile = File(...)):
    """
    Extract the first frame from an uploaded video file and return it as a JPEG image.
    
    Args:
        file: Uploaded video file
        
    Returns:
        StreamingResponse: First frame as JPEG image
    """
    # Validate file type - check both content type and file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp']
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    
    is_valid_content_type = file.content_type and file.content_type.startswith('video/')
    is_valid_extension = file_extension in valid_extensions
    
    if not (is_valid_content_type or is_valid_extension):
        raise HTTPException(
            status_code=400, 
            detail=f"File must be a video. Supported formats: {', '.join(valid_extensions)}"
        )
    
    try:
        # Read the uploaded file content
        contents = await file.read()
        
        # Create a temporary file to store the video
        # This approach is more reliable than in-memory processing for various video formats
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Open video file with OpenCV
            cap = cv2.VideoCapture(temp_file_path)
            
            if not cap.isOpened():
                raise HTTPException(status_code=400, detail="Could not open video file")
            
            # Read the first frame
            success, frame = cap.read()
            cap.release()
            
            if not success or frame is None:
                raise HTTPException(status_code=400, detail="Could not read the first frame from the video")
            
            # Encode frame as JPEG with high quality for better results
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
            success, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            if not success:
                raise HTTPException(status_code=500, detail="Could not encode frame as JPEG")
            
            # Convert to bytes
            frame_bytes = buffer.tobytes()
            
            # Return as streaming response
            return StreamingResponse(
                io.BytesIO(frame_bytes), 
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": f"inline; filename=first_frame_{file.filename}.jpg"
                }
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/extract-first-frame-info/")
async def extract_first_frame_with_info(file: UploadFile = File(...)):
    """
    Extract the first frame from an uploaded video and return both the image and video metadata.
    
    Args:
        file: Uploaded video file
        
    Returns:
        dict: Contains image data (base64) and video information
    """
    import base64
    
    # Validate file type - check both content type and file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp']
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    
    is_valid_content_type = file.content_type and file.content_type.startswith('video/')
    is_valid_extension = file_extension in valid_extensions
    
    if not (is_valid_content_type or is_valid_extension):
        raise HTTPException(
            status_code=400, 
            detail=f"File must be a video. Supported formats: {', '.join(valid_extensions)}"
        )
    
    try:
        # Read the uploaded file content
        contents = await file.read()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Open video file with OpenCV
            cap = cv2.VideoCapture(temp_file_path)
            
            if not cap.isOpened():
                raise HTTPException(status_code=400, detail="Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Read the first frame
            success, frame = cap.read()
            cap.release()
            
            if not success or frame is None:
                raise HTTPException(status_code=400, detail="Could not read the first frame from the video")
            
            # Encode frame as JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
            success, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            if not success:
                raise HTTPException(status_code=500, detail="Could not encode frame as JPEG")
            
            # Convert to base64
            frame_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
            
            return {
                "image_base64": frame_base64,
                "video_info": {
                    "filename": file.filename,
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "file_size_bytes": len(contents)
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
