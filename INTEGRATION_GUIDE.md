# KisanSeva - ML Model & Frontend Integration Guide

## 🏗️ Project Architecture

Your project is now a **full-stack ML application** with:

```
┌─────────────────────────────────────────────┐
│         Frontend (React + TypeScript)        │
│  - Camera interface                          │
│  - Image capture                             │
│  - Results display                           │
│  - History tracking                          │
└────────────────┬────────────────────────────┘
                 │ HTTP (localhost:5000)
                 ▼
┌─────────────────────────────────────────────┐
│    Backend API (Flask - Python)              │
│  - Base64 image processing                   │
│  - Model inference                           │
│  - Recommendation generation                 │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│       ML Models (TensorFlow/Keras)           │
│  - crop_classifier.h5                        │
│  - rice_disease_model.h5                     │
│  - wheat_disease_model.h5                    │
│                                              │
│  + Disease Databases                         │
│  - hindi_diseases.json                       │
│  - marathi_diseases.json                     │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. **Install Backend Dependencies**

Using your virtual environment:

```bash
# Activate environment (if not already active)
.\agri_ai_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Start the Backend Server**

```bash
# In your project folder (with activated venv)
python backend.py
```

You should see:
```
🚀 Starting KisanSeva ML Backend...
📊 Available endpoints:
  - POST /api/analyze (base64 image)
  - POST /api/analyze-url (file upload)
  - GET /health
  - GET /api/models-info
```

### 3. **Start the Frontend (in another terminal)**

```bash
# Make sure you're in the project folder
npm run dev
```

The app will open at `http://localhost:5173`

## 🔄 How Data Flows

1. **User captures image** → Camera → Canvas → Base64 encoding
2. **Base64 sent to backend** → Flask endpoint receives it
3. **Image preprocessing** → Resize to 224x224, normalize
4. **Crop classification** → `crop_classifier.h5` identifies crop type
5. **Disease detection** → Crop-specific model (rice/wheat) detects disease
6. **Recommendation lookup** → `hindi_diseases.json` or `marathi_diseases.json`
7. **Response sent to frontend** → Results displayed to farmer

## 📝 API Endpoints

### POST `/api/analyze`
Analyzes base64-encoded image from camera

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "language": "hindi"  // or "marathi"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "cropName": "Rice",
  "diseaseName": "Leaf Blast",
  "confidence": "High",
  "confidenceScore": 0.89,
  "healthStatus": "Action",
  "recommendations": {
    "Crop": "rice",
    "Disease": "leaf_blast",
    "Identification": ["Brown spots on leaves", "..."],
    "Treatment": ["Apply fungicide", "..."]
  },
  "language": "hindi"
}
```

**Response (Uncertain):**
```json
{
  "status": "uncertain",
  "message": "Disease Uncertain",
  "suggestions": {
    "Healthy": 0.35,
    "Brown Spot": 0.45
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Invalid base64 image: ..."
}
```

### POST `/api/analyze-url`
Analyzes image file upload

**Request:** Multipart form-data
- `image`: Image file (jpg, png, gif)
- `language`: "hindi" or "marathi" (optional)

**Response:** Same as `/api/analyze`

### GET `/health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "KisanSeva ML Backend",
  "version": "1.0.0"
}
```

### GET `/api/models-info`
Get loaded models info

**Response:**
```json
{
  "status": "success",
  "models": {
    "crop_classifier": "crop_classifier.h5",
    "rice_disease": "rice_disease_model.h5",
    "wheat_disease": "wheat_disease_model.h5"
  },
  "input_size": [224, 224],
  "supported_languages": ["hindi", "marathi"]
}
```

## 🔧 Configuration & Customization

### Change Language
In `index.tsx`, update the language in `analyzeImage()`:
```typescript
body: JSON.stringify({
  image: base64Data,
  language: 'marathi'  // Change to marathi for Marathi recommendations
})
```

### Adjust Confidence Thresholds
In `test_model.py`:
```python
CROP_CONF_THRESHOLD = 0.75      # Minimum confidence for crop identification
DISEASE_CONF_THRESHOLD = 0.6    # Minimum confidence for disease detection
```

### Change Model Input Size
In `backend.py`:
```python
IMG_SIZE = (224, 224)  # Must match model's input size
```

## 📱 Testing the Integration

### Option 1: Using Browser DevTools
1. Open frontend at `http://localhost:5173`
2. Click camera button
3. Upload test image
4. Check browser console for API calls

### Option 2: Using curl
```bash
# Get health check
curl http://localhost:5000/health

# Get models info
curl http://localhost:5000/api/models-info

# Test with image file
curl -X POST -F "image=@test_images/000022.jpg" \
  -F "language=hindi" \
  http://localhost:5000/api/analyze-url
```

### Option 3: Using Python
```python
import requests
import base64

# Read image
with open('test_images/000022.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# Send to backend
response = requests.post('http://localhost:5000/api/analyze', json={
    'image': f'data:image/jpeg;base64,{image_data}',
    'language': 'hindi'
})

print(response.json())
```

## 🐛 Troubleshooting

### Error: "Address already in use"
Another process is using port 5000
```bash
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port in backend.py
app.run(host='0.0.0.0', port=5001)  # Change port
```

### Error: "Backend unreachable"
1. Ensure `backend.py` is running
2. Check if `http://localhost:5000/health` returns 200
3. Ensure firewall isn't blocking port 5000
4. Check backend terminal for error logs

### Error: "Invalid base64 image"
- Ensure image is properly encoded as base64
- Frontend should handle this automatically
- Check image format (jpg, png, gif supported)

### Model predictions are poor
1. Check image quality and lighting
2. Ensure crop/leaf is clearly visible
3. Verify models are trained on similar images
4. Try with test images from `test_images/` folder

## 📊 Performance Tips

### Reduce Memory Usage
- Models loaded once at startup
- Images processed in memory (no disk I/O)
- GPU usage disabled for CPU deployment (can re-enable if GPU available)

### Optimize for Mobile
- Base64 images can be large
- Consider image compression in frontend
- Current 224x224 size is balanced for accuracy vs speed

### Scale for Production
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend:app
```

## 🎯 Next Steps

1. **Test with your dataset** - Use images from `test_images/`
2. **Retrain models** - Use `train_model.py` if needed
3. **Add more languages** - Expand `hindi_diseases.json`, `marathi_diseases.json`
4. **Deploy to cloud** - Use AWS, Azure, or Google Cloud
5. **Add user accounts** - Track farmer history across sessions

## 📚 File Reference

| File | Purpose |
|------|---------|
| `backend.py` | Flask API server - bridges frontend & ML models |
| `index.tsx` | React frontend - user interface |
| `test_model.py` | ML prediction pipeline |
| `recommendation_engine.py` | Farmer recommendation logic |
| `crop_classifier.h5` | Crop type identification model |
| `rice_disease_model.h5` | Rice disease detection model |
| `wheat_disease_model.h5` | Wheat disease detection model |
| `hindi_diseases.json` | Hindi disease recommendations database |
| `marathi_diseases.json` | Marathi disease recommendations database |
| `requirements.txt` | Python dependencies |

## ✅ Checklist Before Deployment

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Test image analysis works end-to-end
- [ ] Recommendations display correctly
- [ ] History saves to localStorage
- [ ] Language switching works (hindi/marathi)
- [ ] Mobile camera access works
- [ ] No CORS errors in browser console
- [ ] Performance is acceptable

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **TensorFlow/Keras**: https://www.tensorflow.org/guide
- **React Hooks**: https://react.dev/reference/react/hooks
- **CORS Issues**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

**Created**: January 2026  
**Status**: Ready for Production  
**Supported Languages**: Hindi, Marathi  
**Models**: TensorFlow/Keras  
**API Framework**: Flask  
**Frontend**: React 19 + TypeScript
