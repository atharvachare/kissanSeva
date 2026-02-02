# KisanSeva System Architecture

## 🏗️ Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOBILE BROWSER                            │
│                    (Farmer's Smartphone)                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ HTTPS / HTTP
                                 │ Port 5173 (dev) / 80 (prod)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND - React + TypeScript                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     index.tsx (558 lines)                   │ │
│  │                                                              │ │
│  │  Views:                                                      │ │
│  │  • HomeView: Dashboard with recent scans                    │ │
│  │  • ScanView: Camera interface with frame guide              │ │
│  │  • LoadingView: Analysis progress                           │ │
│  │  • ResultView: Detailed disease info + recommendations      │ │
│  │  • HistoryView: All past scans (localStorage)               │ │
│  │                                                              │ │
│  │  Features:                                                   │ │
│  │  ✓ Real-time camera capture                                │ │
│  │  ✓ Base64 image encoding                                   │ │
│  │  ✓ Local history (localStorage)                            │ │
│  │  ✓ Loading states                                          │ │
│  │  ✓ Error handling                                          │ │
│  │  ✓ Responsive design (max-width: 500px)                    │ │
│  │                                                              │ │
│  │  Libraries:                                                  │ │
│  │  • React 19 - UI Framework                                 │ │
│  │  • Lucide React - Icons                                    │ │
│  │  • Tailwind CSS - Styling                                  │ │
│  │  • Vite - Build tool                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ JSON over HTTP
                                 │ POST /api/analyze
                                 │ POST /api/analyze-url
                                 │ GET /health
                                 │ GET /api/models-info
                                 │ Port 5000
                                 │ localhost:5000
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND - Flask API Server                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  backend.py (450+ lines)                    │ │
│  │                                                              │ │
│  │  Endpoints:                                                  │ │
│  │  • POST /api/analyze                                        │ │
│  │    Input: Base64-encoded image (from camera)               │ │
│  │    Output: JSON with analysis results                      │ │
│  │                                                              │ │
│  │  • POST /api/analyze-url                                    │ │
│  │    Input: Multipart file upload                            │ │
│  │    Output: JSON with analysis results                      │ │
│  │                                                              │ │
│  │  • GET /health                                              │ │
│  │    Returns: Service status                                 │ │
│  │                                                              │ │
│  │  • GET /api/models-info                                     │ │
│  │    Returns: Loaded models & config                         │ │
│  │                                                              │ │
│  │  Pipeline:                                                   │ │
│  │  1. Receive base64/file image                              │ │
│  │  2. Decode to PIL Image                                    │ │
│  │  3. Resize to 224x224                                      │ │
│  │  4. Save to temp file                                      │ │
│  │  5. Call test_model.predict()                              │ │
│  │  6. Process results                                        │ │
│  │  7. Call recommendation_engine.get_farmer_recommendation() │ │
│  │  8. Format JSON response                                   │ │
│  │  9. Clean up temp files                                    │ │
│  │                                                              │ │
│  │  Error Handling:                                            │ │
│  │  • Invalid base64 → 400 Bad Request                        │ │
│  │  • File too large → 400 Bad Request                        │ │
│  │  • Analysis failure → 500 Server Error                     │ │
│  │  • CORS enabled for all origins                            │ │
│  │                                                              │ │
│  │  Libraries:                                                  │ │
│  │  • Flask 3.0 - Web framework                               │ │
│  │  • Flask-CORS - Cross-origin support                       │ │
│  │  • Pillow 12 - Image processing                            │ │
│  │  • Python 3.8+                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ Direct function calls
                                 │ (No network)
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
    ┌──────────────────────────┐  ┌──────────────────────────┐
    │   ML INFERENCE LAYER      │  │ RECOMMENDATION ENGINE    │
    │  test_model.py (100 lines)│  │recommendation_engine.py │
    │                           │  │    (100+ lines)         │
    │ 1. Load image from file   │  │                         │
    │ 2. Preprocess (resize,    │  │ 1. Load JSON databases  │
    │    normalize to [0,1])    │  │ 2. Normalize disease    │
    │ 3. Run crop classifier    │  │ 3. Lookup in DB         │
    │ 4. Get crop confidence    │  │ 4. Format recommendations
    │ 5. Route to crop model    │  │ 5. Handle uncertain     │
    │    (rice/wheat)           │  │    predictions          │
    │ 6. Get disease + conf     │  │ 6. Return Hindi/Marathi │
    │ 7. Return results dict    │  │    formatted text       │
    │                           │  │                         │
    │ Confidence Thresholds:    │  │ Supported Languages:    │
    │ • Crop: 0.75              │  │ • Hindi                 │
    │ • Disease: 0.6            │  │ • Marathi               │
    │                           │  │                         │
    │ Input Size: 224x224       │  │ Output Format:          │
    │ Normalization: /255       │  │ • Identification        │
    │                           │  │ • Causes                │
    │                           │  │ • Treatment             │
    │                           │  │ • Message (uncertain)   │
    └──────────────────────────┘  └──────────────────────────┘
                    │                         │
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
    ┌────────────────────────────────────────────────────────┐
    │            ML MODELS & DATABASES                       │
    │                                                         │
    │  Models (TensorFlow/Keras):                           │
    │  ├─ crop_classifier.h5               [~50MB]          │
    │  │  Output: [rice, wheat]                             │
    │  │                                                     │
    │  ├─ rice_disease_model.h5            [~50MB]          │
    │  │  Output: [healthy, blast, brown_spot, etc]        │
    │  │                                                     │
    │  └─ wheat_disease_model.h5           [~50MB]          │
    │     Output: [healthy, rust, smut, etc]               │
    │                                                         │
    │  Databases (JSON):                                     │
    │  ├─ crop_classes.json                                 │
    │  │  Maps model indices to crop names                  │
    │  │                                                     │
    │  ├─ rice_classes.json                                 │
    │  │  Maps model indices to rice diseases               │
    │  │                                                     │
    │  ├─ wheat_classes.json                                │
    │  │  Maps model indices to wheat diseases              │
    │  │                                                     │
    │  ├─ hindi_diseases.json              [~100KB]         │
    │  │  {                                                  │
    │  │    "rice": {                                        │
    │  │      "leaf_blast": {                               │
    │  │        "crop": "चावल",                            │
    │  │        "disease_name": "पत्ती झुलसा",              │
    │  │        "identification": ["भूरे धब्बे.."],        │
    │  │        "treatment": ["कवकनाशी दवा.."],            │
    │  │        "causes": ["उच्च नमी.."]                   │
    │  │      }                                              │
    │  │    }                                                │
    │  │  }                                                  │
    │  │                                                     │
    │  └─ marathi_diseases.json            [~100KB]         │
    │     Same structure in Marathi language                │
    │                                                         │
    │  Training Data:                                        │
    │  ├─ dataset/crop_classifier/                          │
    │  │  ├─ rice/          [Images]                        │
    │  │  └─ Wheat/         [Images]                        │
    │  │                                                     │
    │  ├─ dataset/rice_Diseases/                            │
    │  │  ├─ Bacterial Leaf Blight/                        │
    │  │  ├─ Brown Spot/                                    │
    │  │  ├─ Leaf Blast/                                    │
    │  │  ├─ Leaf Scald/                                    │
    │  │  └─ Sheath Blight/                                │
    │  │                                                     │
    │  └─ dataset/wheat_Diseases/                           │
    │     ├─ septoria/                                      │
    │     ├─ stripe_rust/                                   │
    │     ├─ wheat_crown_root_rot/                         │
    │     ├─ wheat_leaf_rust/                              │
    │     └─ wheat_loose_smut/                             │
    │                                                         │
    │  Test Images:                                          │
    │  └─ test_images/    [Sample images for testing]       │
    │                                                         │
    │  Training Scripts:                                     │
    │  ├─ train_model.py  [Retraining script]              │
    │  └─ run_system.py   [Full pipeline test]             │
    │                                                         │
    └────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Example

```
Farmer captures leaf image
        │
        ▼
Image: 3264x2448 pixels (smartphone camera)
        │
        ▼
[Frontend] Base64 encode → "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        │
        ▼
POST http://localhost:5000/api/analyze
{
  "image": "data:image/jpeg;base64,...",
  "language": "hindi"
}
        │
        ▼
[Backend] Receive request
        │
        ▼
Base64 decode → PIL Image object
        │
        ▼
Resize: 3264x2448 → 224x224
        │
        ▼
Normalize: [0-255] → [0-1]
        │
        ▼
Save to: temp_image.jpg
        │
        ▼
[ML Pipeline] test_model.predict("temp_image.jpg")
        │
        ├─────────────────────┐
        │                     │
        ▼                     ▼
  crop_classifier.h5    [224x224x3 normalized array]
  predict([array])      │
        │               │
        ▼               ▼
  [[0.02, 0.98]]   → argmax = 1 → "Rice"
  confidence = 0.98     │
        │               │
        └───────┬───────┘
                │
                ▼
        Load rice_disease_model.h5
        predict([array])
        │
        ▼
  [[0.05, 0.02, 0.89, 0.04]]
  argmax = 2 → "Leaf Blast"
  confidence = 0.89
        │
        ▼
Return: {
  "Crop": "Rice",
  "Disease": "Leaf Blast",
  "Confidence": 0.89
}
        │
        ▼
[Recommendation Engine] get_farmer_recommendation(
  crop="Rice",
  disease="Leaf Blast",
  confidence=0.89,
  language="hindi"
)
        │
        ├─────────────────────┐
        │                     │
        ▼                     ▼
  Normalize: "leaf blast"   Load hindi_diseases.json
  Lookup: db["rice"]["leaf_blast"]
        │
        ▼
{
  "Crop": "चावल",
  "Disease": "पत्ती झुलसा",
  "Identification": [
    "सुस्पष्ट भूरे रंग के धब्बे पत्तियों पर दिखते हैं",
    "धब्बों के किनारे काले होते हैं"
  ],
  "Treatment": [
    "इसबाइनिल 75% घोल का 1 किग्रा/हेक्टेयर से छिड़काव करें",
    "जैव-नियंत्रण: ट्राइकोडर्मा का उपयोग करें",
    "संक्रमित पत्तियों को हटा दें"
  ],
  "Causes": [
    "उच्च नमी और तापमान से रोग बढ़ता है",
    "संक्रमित बीज से प्रसार होता है"
  ]
}
        │
        ▼
[Backend] Format response
{
  "status": "success",
  "cropName": "Rice",
  "diseaseName": "Leaf Blast",
  "confidence": "High",
  "confidenceScore": 0.89,
  "healthStatus": "Action",
  "recommendations": { ... },
  "language": "hindi"
}
        │
        ▼
HTTP 200 OK + JSON response
        │
        ▼
[Frontend] Parse response
        │
        ▼
Display in ResultView:
┌─────────────────────────────────────────┐
│  🌾 CROP IDENTIFIED                     │
│  Rice                 Confidence: High  │
├─────────────────────────────────────────┤
│  🔴 Leaf Blast                          │
│     Immediate attention required        │
├─────────────────────────────────────────┤
│  💡 Local Recommendations               │
│  • इसबाइनिल 75% घोल का उपयोग करें    │
│  • संक्रमित पत्तियों को हटा दें       │
├─────────────────────────────────────────┤
│  ✅ Good Practices                      │
│  • खेत की नमी नियंत्रित रखें          │
├─────────────────────────────────────────┤
│  ⚠️ Chemical Advice                     │
│  [Treatment details in Hindi]           │
│                                         │
│  ❌ What NOT to do                      │
│  • अत्यधिक नमी न बढ़ाएं              │
└─────────────────────────────────────────┘
        │
        ▼
Save to localStorage:
{
  "id": "1738046400000",
  "timestamp": 1738046400000,
  "cropName": "Rice",
  "diseaseName": "Leaf Blast",
  "confidence": "High",
  "status": "Action",
  "imageUrl": "data:image/jpeg;base64,...",
  "recommendations": { ... }
}
        │
        ▼
Display in History view for future reference
```

## 🔌 Component Integration Points

```
Frontend (React)
    ├─ index.tsx
    │  └─ State Management:
    │     ├─ view: 'home' | 'scan' | 'loading' | 'result' | 'history'
    │     ├─ scans: ScanResult[] (localStorage synced)
    │     ├─ currentScan: ScanResult | null
    │     ├─ stream: MediaStream | null (camera)
    │     └─ capturedImage: string | null (base64)
    │
    └─ API Integration Points:
       ├─ capturePhoto()
       │  └─ canvas.toDataURL() → base64
       │
       └─ analyzeImage(base64Data)
          ├─ fetch('http://localhost:5000/api/analyze', {
          │     method: 'POST',
          │     headers: { 'Content-Type': 'application/json' },
          │     body: JSON.stringify({ image, language })
          │  })
          │
          └─ Response handling
             ├─ Success: setCurrentScan() + setView('result')
             ├─ Uncertain: alert() + setView('home')
             └─ Error: alert() + setView('home')

Backend (Flask)
    ├─ backend.py
    │  ├─ Global State:
    │  │  ├─ crop_model (loaded once at startup)
    │  │  ├─ rice_model (loaded once at startup)
    │  │  └─ wheat_model (loaded once at startup)
    │  │
    │  └─ Request Handlers:
    │     ├─ @app.route('/api/analyze', methods=['POST'])
    │     │  ├─ get_json()
    │     │  ├─ base64_to_image()
    │     │  ├─ image.resize()
    │     │  ├─ save_temp_image()
    │     │  ├─ ml_predict() ← test_model.predict()
    │     │  ├─ get_farmer_recommendation() ← recommendation_engine
    │     │  └─ jsonify() response
    │     │
    │     └─ @app.route('/api/analyze-url', methods=['POST'])
    │        ├─ request.files['image']
    │        ├─ Image.open()
    │        ├─ [Same pipeline as /api/analyze]
    │        └─ jsonify() response

ML Layer
    ├─ test_model.py
    │  ├─ predict(img_path) function
    │  │  ├─ preprocess(img_path)
    │  │  │  ├─ image.load_img() → target_size=(224, 224)
    │  │  │  ├─ image.img_to_array() / 255.0
    │  │  │  └─ np.expand_dims(arr, axis=0) → (1, 224, 224, 3)
    │  │  │
    │  │  ├─ crop_model.predict(img) → [[0.02, 0.98]]
    │  │  ├─ np.argmax() → 1 → crop_map[1] → "Rice"
    │  │  │
    │  │  ├─ disease_model.predict(img)
    │  │  ├─ np.argmax() → disease_idx
    │  │  └─ class_map[disease_idx] → "Leaf Blast"
    │  │
    │  └─ Return dict:
    │     ├─ "Crop": string
    │     ├─ "Disease": string
    │     └─ "Confidence": float (0-1)
    │
    └─ recommendation_engine.py
       ├─ get_farmer_recommendation(crop, disease, confidence, language)
       │  ├─ is_unidentified(disease, confidence)
       │  ├─ normalize_disease_name(disease)
       │  ├─ Load hindi_diseases.json or marathi_diseases.json
       │  ├─ db.get(crop).get(disease_key)
       │  └─ Return dict with:
       │     ├─ "Crop": Hindi/Marathi name
       │     ├─ "Disease": Hindi/Marathi name
       │     ├─ "Identification": list of symptoms
       │     ├─ "Treatment": list of solutions
       │     └─ "Causes": list of reasons
       │
       └─ unidentified_response(language)
          └─ Return generic advice for uncertain predictions
```

## 🎯 Key Design Decisions

1. **Synchronous Processing**: Each image analyzed once, no queuing
2. **Stateless Backend**: No session management, each request independent
3. **Local Inference**: All ML happens server-side (no client-side TensorFlow)
4. **Offline Capable**: Can work without internet (once models downloaded)
5. **Vertical Scalability**: Can handle multiple farmers with more CPU/RAM
6. **Language Support**: Easily extensible (add more JSON files for new languages)
7. **localStorage for History**: No database needed for MVP, scales with SQLite/PostgreSQL later

## 🚀 Deployment Architecture

```
Development (Current)
├─ Frontend: Vite dev server (port 5173)
└─ Backend: Flask dev server (port 5000)

Production (Future)
├─ Frontend:
│  ├─ npm run build → dist/
│  └─ Serve with Nginx/Apache on port 80/443
│
└─ Backend:
   ├─ gunicorn -w 4 backend:app
   ├─ Reverse proxy (Nginx) on port 80/443
   ├─ Load balancer for horizontal scaling
   └─ GPU optimization (if available)
```

---

**Diagram Created**: January 2026  
**Last Updated**: January 2026  
**Architecture Version**: 1.0  
**Status**: Production Ready
