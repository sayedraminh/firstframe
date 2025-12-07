# Next.js Integration Guide for First Frame Extractor API

This guide shows how to integrate the First Frame Extractor FastAPI with a Next.js application.

## 🚀 Quick Start

### 1. Basic Video Upload Component

Create a React component that uploads videos to your FastAPI backend:

```jsx
// components/VideoFrameExtractor.jsx
import { useState } from 'react';

export default function VideoFrameExtractor() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [extractedFrame, setExtractedFrame] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI URL

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const extractFirstFrame = async (withInfo = false) => {
    if (!selectedFile) {
      setError('Please select a video file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const endpoint = withInfo 
        ? '/extract-first-frame-info/' 
        : '/extract-first-frame/';

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to extract frame');
      }

      if (withInfo) {
        // Handle JSON response with video info
        const data = await response.json();
        setVideoInfo(data.video_info);
        
        // Convert base64 to blob URL for display
        const imageBlob = new Blob([
          new Uint8Array(
            atob(data.image_base64)
              .split('')
              .map(char => char.charCodeAt(0))
          )
        ], { type: 'image/jpeg' });
        
        setExtractedFrame(URL.createObjectURL(imageBlob));
      } else {
        // Handle image response
        const blob = await response.blob();
        setExtractedFrame(URL.createObjectURL(blob));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">
        Video First Frame Extractor
      </h2>

      {/* File Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Video File
        </label>
        <input
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500 
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => extractFirstFrame(false)}
          disabled={!selectedFile || loading}
          className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg
                     hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Extract Frame Only'}
        </button>
        
        <button
          onClick={() => extractFirstFrame(true)}
          disabled={!selectedFile || loading}
          className="flex-1 bg-green-500 text-white py-2 px-4 rounded-lg
                     hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Extract Frame + Info'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Error: {error}
        </div>
      )}

      {/* Results */}
      {extractedFrame && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Extracted First Frame:</h3>
          <img
            src={extractedFrame}
            alt="First frame"
            className="w-full max-w-md mx-auto rounded-lg shadow-md"
          />
          
          {/* Video Info */}
          {videoInfo && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Video Information:</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><strong>Dimensions:</strong> {videoInfo.width}x{videoInfo.height}</div>
                <div><strong>FPS:</strong> {videoInfo.fps?.toFixed(2)}</div>
                <div><strong>Duration:</strong> {videoInfo.duration_seconds?.toFixed(2)}s</div>
                <div><strong>Frames:</strong> {videoInfo.frame_count}</div>
                <div><strong>File Size:</strong> {(videoInfo.file_size_bytes / 1024 / 1024)?.toFixed(2)} MB</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

## 🎨 Advanced Implementation with TypeScript

### 2. TypeScript Version with Better Error Handling

```tsx
// components/VideoFrameExtractor.tsx
import React, { useState, useCallback } from 'react';

interface VideoInfo {
  filename: string;
  width: number;
  height: number;
  fps: number;
  frame_count: number;
  duration_seconds: number;
  file_size_bytes: number;
}

interface ExtractResponse {
  image_base64: string;
  video_info: VideoInfo;
}

interface ExtractorState {
  selectedFile: File | null;
  extractedFrame: string | null;
  videoInfo: VideoInfo | null;
  loading: boolean;
  error: string | null;
  processingTime: number | null;
}

const VideoFrameExtractor: React.FC = () => {
  const [state, setState] = useState<ExtractorState>({
    selectedFile: null,
    extractedFrame: null,
    videoInfo: null,
    loading: false,
    error: null,
    processingTime: null,
  });

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const resetState = useCallback(() => {
    setState(prev => ({
      ...prev,
      extractedFrame: null,
      videoInfo: null,
      error: null,
      processingTime: null,
    }));
  }, []);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setState(prev => ({
        ...prev,
        selectedFile: file,
        error: null,
      }));
      resetState();
    }
  }, [resetState]);

  const extractFirstFrame = useCallback(async (withInfo = false) => {
    if (!state.selectedFile) {
      setState(prev => ({ ...prev, error: 'Please select a video file first' }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const formData = new FormData();
      formData.append('file', state.selectedFile);

      const endpoint = withInfo 
        ? '/extract-first-frame-info/' 
        : '/extract-first-frame/';

      const startTime = performance.now();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to extract frame`);
      }

      if (withInfo) {
        const data: ExtractResponse = await response.json();
        
        // Convert base64 to blob URL
        const binaryString = atob(data.image_base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        const imageBlob = new Blob([bytes], { type: 'image/jpeg' });
        const imageUrl = URL.createObjectURL(imageBlob);

        setState(prev => ({
          ...prev,
          extractedFrame: imageUrl,
          videoInfo: data.video_info,
          processingTime,
        }));
      } else {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        setState(prev => ({
          ...prev,
          extractedFrame: imageUrl,
          processingTime,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'An unknown error occurred',
      }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [state.selectedFile, API_BASE_URL]);

  // Cleanup blob URLs when component unmounts
  React.useEffect(() => {
    return () => {
      if (state.extractedFrame) {
        URL.revokeObjectURL(state.extractedFrame);
      }
    };
  }, [state.extractedFrame]);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">
        🎬 Video First Frame Extractor
      </h2>

      {/* File Upload Section */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Video File (.mp4, .avi, .mov, .mkv, .webm)
        </label>
        <div className="relative">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 
                       file:mr-4 file:py-3 file:px-6
                       file:rounded-lg file:border-0
                       file:text-sm file:font-semibold
                       file:bg-blue-50 file:text-blue-700
                       hover:file:bg-blue-100 transition-colors"
          />
        </div>
        {state.selectedFile && (
          <p className="mt-2 text-sm text-gray-600">
            Selected: {state.selectedFile.name} ({(state.selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <button
          onClick={() => extractFirstFrame(false)}
          disabled={!state.selectedFile || state.loading}
          className="bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold
                     hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                     transition-colors duration-200 flex items-center justify-center"
        >
          {state.loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </div>
          ) : (
            '🖼️ Extract Frame Only'
          )}
        </button>
        
        <button
          onClick={() => extractFirstFrame(true)}
          disabled={!state.selectedFile || state.loading}
          className="bg-green-600 text-white py-3 px-6 rounded-lg font-semibold
                     hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                     transition-colors duration-200 flex items-center justify-center"
        >
          {state.loading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </div>
          ) : (
            '📊 Extract Frame + Info'
          )}
        </button>
      </div>

      {/* Processing Time */}
      {state.processingTime && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm">
            ⚡ Processing completed in {state.processingTime.toFixed(0)}ms
          </p>
        </div>
      )}

      {/* Error Display */}
      {state.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-800 rounded-lg">
          <div className="flex items-center">
            <span className="text-lg mr-2">❌</span>
            <span className="font-semibold">Error:</span>
          </div>
          <p className="mt-1">{state.error}</p>
        </div>
      )}

      {/* Results */}
      {state.extractedFrame && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">
              📸 Extracted First Frame
            </h3>
            <div className="inline-block border-4 border-gray-200 rounded-lg overflow-hidden shadow-lg">
              <img
                src={state.extractedFrame}
                alt="First frame of video"
                className="max-w-full h-auto max-h-96 object-contain"
              />
            </div>
          </div>
          
          {/* Video Information */}
          {state.videoInfo && (
            <div className="bg-gray-50 p-6 rounded-lg border">
              <h4 className="text-lg font-semibold mb-4 text-gray-800 flex items-center">
                📹 Video Information
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">Dimensions</div>
                  <div className="font-semibold">{state.videoInfo.width} × {state.videoInfo.height}</div>
                </div>
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">Frame Rate</div>
                  <div className="font-semibold">{state.videoInfo.fps.toFixed(2)} FPS</div>
                </div>
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">Duration</div>
                  <div className="font-semibold">{state.videoInfo.duration_seconds.toFixed(2)}s</div>
                </div>
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">Total Frames</div>
                  <div className="font-semibold">{state.videoInfo.frame_count.toLocaleString()}</div>
                </div>
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">File Size</div>
                  <div className="font-semibold">
                    {(state.videoInfo.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
                <div className="bg-white p-3 rounded border">
                  <div className="text-sm text-gray-600">Filename</div>
                  <div className="font-semibold text-xs truncate">{state.videoInfo.filename}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoFrameExtractor;
```

## 🔧 Environment Configuration

### 3. Environment Variables

Create a `.env.local` file in your Next.js project:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```bash
# .env.production.local
NEXT_PUBLIC_API_URL=https://your-fastapi-domain.com
```

## 🚀 Next.js API Route (Optional)

### 4. Proxy API Route for Better Security

Create `pages/api/extract-frame.js` (or `app/api/extract-frame/route.js` for App Router):

```javascript
// pages/api/extract-frame.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const formData = new FormData();
    
    // Forward the file from client to FastAPI
    const response = await fetch(`${process.env.FASTAPI_URL}/extract-first-frame/`, {
      method: 'POST',
      body: req.body, // Forward the form data
      headers: {
        ...req.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`FastAPI responded with ${response.status}`);
    }

    const buffer = await response.arrayBuffer();
    
    res.setHeader('Content-Type', 'image/jpeg');
    res.setHeader('Content-Length', buffer.byteLength);
    res.send(Buffer.from(buffer));
    
  } catch (error) {
    console.error('API Route Error:', error);
    res.status(500).json({ error: 'Failed to extract frame' });
  }
}

export const config = {
  api: {
    bodyParser: false, // Disable body parsing for file uploads
  },
};
```

## 🎨 Styling with Tailwind CSS

### 5. Install Tailwind CSS (if not already installed)

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Configure `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## 🔒 CORS Configuration

### 6. Update FastAPI for CORS (if needed)

Add to your `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Add your Next.js URLs
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📱 Usage in Next.js Pages

### 7. Using the Component

```jsx
// pages/index.js
import VideoFrameExtractor from '../components/VideoFrameExtractor';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-8">
          Video Frame Extractor
        </h1>
        <VideoFrameExtractor />
      </div>
    </div>
  );
}
```

## 🚀 Deployment Considerations

### 8. Production Deployment

1. **FastAPI Backend**: Deploy on services like Railway, Heroku, or DigitalOcean
2. **Next.js Frontend**: Deploy on Vercel, Netlify, or any hosting service
3. **Environment Variables**: Update `NEXT_PUBLIC_API_URL` to your production FastAPI URL
4. **File Size Limits**: Consider adding file size validation in both frontend and backend
5. **Rate Limiting**: Implement rate limiting on your FastAPI endpoints

### 9. Performance Optimizations

```jsx
// Add file size validation
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (file.size > MAX_FILE_SIZE) {
      setError('File size must be less than 100MB');
      return;
    }
    setSelectedFile(file);
    setError(null);
  }
};
```

## 🎉 Complete Example

Your FastAPI is now ready to work with Next.js! The integration provides:

- ✅ **Fast video processing** (your current API processes in ~0.1 seconds)
- ✅ **Modern React UI** with loading states and error handling
- ✅ **TypeScript support** for better development experience
- ✅ **Responsive design** that works on all devices
- ✅ **Production-ready** with proper error handling and cleanup

Start your FastAPI server (`python main.py`) and integrate this component into your Next.js app for a complete video frame extraction solution! 🚀
