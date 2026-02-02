# 🚀 KisanSeva Quick Start

## ⚡ 30-Second Setup

### Terminal 1: Start Backend
```bash
.\agri_ai_env\Scripts\activate
python backend.py
```

### Terminal 2: Start Frontend
```bash
npm run dev
```

That's it! 🎉

## 📱 How to Use

1. Open `http://localhost:5173` in browser
2. Click **Camera** button at bottom
3. Point at crop leaf
4. Click **Capture**
5. Wait for analysis
6. See recommendations

## 🔗 What Changed

| Before | After |
|--------|-------|
| Used Google Gemini AI | Uses your ML models |
| No local processing | Full local ML inference |
| Required internet API key | Offline capable |
| Generic advice | Farmer-specific recommendations (Hindi/Marathi) |

## 📊 Project Structure

```
KissanX/
├── index.tsx                 ← React Frontend
├── backend.py               ← Flask API (NEW)
├── test_model.py            ← ML Pipeline
├── recommendation_engine.py  ← Farmer Advice
│
├── crop_classifier.h5       ← Crop Detection Model
├── rice_disease_model.h5    ← Rice Disease Model
├── wheat_disease_model.h5   ← Wheat Disease Model
│
├── hindi_diseases.json      ← Hindi Recommendations
├── marathi_diseases.json    ← Marathi Recommendations
│
├── INTEGRATION_GUIDE.md     ← Full Documentation (NEW)
├── requirements.txt         ← Python Dependencies (NEW)
└── start_backend.bat        ← Auto-Start Script (NEW)
```

## 🧪 Test Integration

```bash
# After starting backend, in new terminal:
python test_integration.py
```

Shows: ✓ Backend running, ✓ Models loaded, ✓ Analysis works

## ⚙️ Configure

### Change Language (Hindi → Marathi)
Edit `index.tsx` line ~142:
```typescript
language: 'marathi'  // Change from 'hindi'
```

### Adjust Confidence Thresholds
Edit `test_model.py`:
```python
CROP_CONF_THRESHOLD = 0.75      # Crop certainty
DISEASE_CONF_THRESHOLD = 0.6    # Disease certainty
```

### Use Different Port
Edit `backend.py` last line:
```python
app.run(host='0.0.0.0', port=5001)  # Change from 5000
```

Also update `index.tsx` line ~133:
```typescript
fetch('http://localhost:5001/api/analyze', {  // Change from 5000
```

## 🐛 Common Issues

### "Cannot connect to localhost:5000"
- ✓ Did you run `python backend.py`?
- ✓ Is terminal showing models loaded?

### "Address already in use"
```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <number> /F
```

### Models loading slow
- Normal - TensorFlow loads ~30 seconds first time
- Will be faster on second run

### Backend crashes
- Check `test_model.py` - models may be corrupted
- Try re-training or re-downloading models

## 📦 Install New Dependencies

```bash
# Backend (Python)
.\agri_ai_env\Scripts\activate
pip install package_name

# Frontend (NPM)
npm install package_name
```

## 📚 Documentation

- **Full Guide**: `INTEGRATION_GUIDE.md`
- **API Details**: `INTEGRATION_GUIDE.md` → API Endpoints
- **Architecture**: `INTEGRATION_GUIDE.md` → Project Architecture
- **Troubleshooting**: `INTEGRATION_GUIDE.md` → Troubleshooting

## 🎯 Next Steps

1. ✅ Test with sample images (`test_images/`)
2. 📱 Test on mobile (must be on same network)
3. 🔄 Retrain models with your own data (`train_model.py`)
4. 🌐 Deploy to cloud (AWS/Azure/Google)
5. 👥 Add user accounts & backend database

## 💡 Pro Tips

- **Keep backend terminal open** - shows real-time logs
- **Check browser console** (F12) for frontend errors
- **Use test images** to verify without camera
- **Monitor response times** - aim for <5 seconds analysis

## 🤔 FAQ

**Q: Can I use this offline?**  
A: Yes! Everything runs locally. No internet needed.

**Q: Why does first analysis take longer?**  
A: Models load into memory on first use (~30 sec). Subsequent analyses are faster.

**Q: Can I add more crops/diseases?**  
A: Yes, retrain models and update JSON files. See `train_model.py`.

**Q: How accurate are predictions?**  
A: Depends on training data. Test with your crop images.

**Q: Can I deploy this?**  
A: Yes! See INTEGRATION_GUIDE.md → Scale for Production

---

**Status**: ✅ Ready to Use  
**Models**: Loaded & Connected  
**Frontend**: Updated & Integrated  
**Language Support**: Hindi, Marathi  

Happy farming! 🌾
