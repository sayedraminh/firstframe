# First Frame Video Extractor

A high-performance FastAPI application that extracts the first frame from uploaded video files and returns it as a JPEG image with minimal latency.

## Features

- **Fast Processing**: Optimized for speed using OpenCV and efficient file handling
- **Multiple Endpoints**: 
  - `/extract-first-frame/` - Returns first frame as image
  - `/extract-first-frame-info/` - Returns first frame + video metadata
- **Format Support**: Supports all major video formats (MP4, AVI, MOV, MKV, etc.)
- **Error Handling**: Comprehensive error handling and validation
- **Async Processing**: Built with FastAPI's async capabilities for concurrent requests

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd firstframevid
   ```

2. **Activate your virtual environment** (if using one):
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Server
```bash
python main.py
```

### Production Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Railway Deployment

This repo includes both Railway builder configs:

- `railpack.json` for Railway's default Railpack builder
- `nixpacks.toml` for legacy Nixpacks deployments

Both configs install the system `ffmpeg` package, which provides `ffmpeg` and
`ffprobe`, and start the app with Railway's assigned port:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## API Endpoints

### 1. Extract First Frame (Image Response)
**POST** `/extract-first-frame/`

Uploads a video file and returns the first frame as a JPEG image.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Video file (key: "file")

**Response:**
- Content-Type: image/jpeg
- Body: JPEG image data

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/extract-first-frame/" \
     -H "accept: image/jpeg" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_video.mp4" \
     --output first_frame.jpg
```

### 2. Extract First Frame with Video Info (JSON Response)
**POST** `/extract-first-frame-info/`

Uploads a video file and returns the first frame as base64 along with video metadata.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Video file (key: "file")

**Response:**
```json
{
  "image_base64": "base64_encoded_image_data",
  "video_info": {
    "filename": "video.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "frame_count": 900,
    "duration_seconds": 30.0,
    "file_size_bytes": 15728640
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/extract-first-frame-info/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_video.mp4"
```

### 3. Health Check
**GET** `/`

Returns API status.

**Response:**
```json
{
  "message": "First Frame Extractor API is running"
}
```

## Interactive API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive documentation where you can test the endpoints directly from your browser.

## Performance Optimizations

The application is optimized for speed through:

1. **Efficient File Handling**: Uses temporary files for reliable video processing
2. **OpenCV Optimization**: Leverages OpenCV's optimized video decoding
3. **Async Processing**: FastAPI's async capabilities for handling multiple requests
4. **Resource Management**: Proper cleanup of temporary files and video capture objects
5. **High-Quality JPEG Encoding**: Balances file size and image quality

## Supported Video Formats

The application supports all video formats that OpenCV can handle, including:
- MP4
- AVI
- MOV
- MKV
- WMV
- FLV
- WebM
- And many more...

## Error Handling

The API provides clear error messages for common issues:
- Invalid file types (non-video files)
- Corrupted video files
- Videos without readable frames
- Server errors during processing

## Example Python Client

```python
import requests

def extract_first_frame(video_path, output_path):
    url = "http://localhost:8000/extract-first-frame/"
    
    with open(video_path, "rb") as video_file:
        files = {"file": video_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        with open(output_path, "wb") as output_file:
            output_file.write(response.content)
        print(f"First frame saved to {output_path}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Usage
extract_first_frame("input_video.mp4", "first_frame.jpg")
```

## License

This project is open source and available under the MIT License.
