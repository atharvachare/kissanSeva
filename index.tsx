
import React, { useState, useRef, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { 
  Camera, 
  Home, 
  History, 
  Leaf, 
  ChevronRight, 
  AlertCircle, 
  CheckCircle2, 
  Info, 
  Droplet, 
  Sun, 
  Zap, 
  X, 
  RefreshCcw,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';

// --- Constants & Types ---

const COLORS = {
  primary: '#1B4332',
  secondary: '#2D6A4F',
  accent: '#52B788',
  bg: '#F0FFF4',
  text: '#1B4332',
  muted: '#748E81'
};

interface ScanResult {
  id: string;
  timestamp: number;
  cropName: string;
  diseaseName: string;
  confidence: 'High' | 'Medium' | 'Low';
  status: 'Healthy' | 'Monitor' | 'Action';
  imageUrl: string;
  recommendations: {
    traditional: string[];
    bestPractices: string[];
    chemical: string;
    whatNotToDo: string[];
  };
}

// --- Components ---

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  className = '', 
  disabled = false,
  icon: Icon
}: any) => {
  const variants = {
    primary: 'bg-[#1B4332] text-white active:bg-[#081C15]',
    secondary: 'bg-[#D8F3DC] text-[#1B4332] active:bg-[#B7E4C7]',
    outline: 'border-2 border-[#1B4332] text-[#1B4332] active:bg-[#F0FFF4]',
    ghost: 'text-[#1B4332] active:bg-[#F0FFF4]'
  };

  return (
    <button 
      disabled={disabled}
      onClick={onClick}
      className={`flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl font-semibold transition-all duration-200 disabled:opacity-50 ${variants[variant as keyof typeof variants]} ${className}`}
    >
      {Icon && <Icon size={20} />}
      {children}
    </button>
  );
};

const Card = ({ children, className = "", onClick }: any) => (
  <div 
    onClick={onClick}
    className={`bg-white rounded-3xl p-5 shadow-sm border border-[#E9F5ED] ${className}`}
  >
    {children}
  </div>
);

const App = () => {
  const [view, setView] = useState<'home' | 'scan' | 'loading' | 'result' | 'history' | 'upload'>('home');
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [currentScan, setCurrentScan] = useState<ScanResult | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load history from local storage
  useEffect(() => {
    const saved = localStorage.getItem('kisanseva_history');
    if (saved) setScans(JSON.parse(saved));
  }, []);

  useEffect(() => {
    if (scans.length > 0) {
      localStorage.setItem('kisanseva_history', JSON.stringify(scans));
    }
  }, [scans]);

  const startCamera = async () => {
    try {
      setError(null);
      const s = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      setStream(s);
      if (videoRef.current) videoRef.current.srcObject = s;
      setView('scan');
    } catch (err: any) {
      console.error("Camera error:", err);
      setError("Camera access denied. Please use upload instead.");
      alert("Camera not available. You can upload an image instead.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const handleFileUpload = (event: any) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      const base64Data = e.target.result;
      setCapturedImage(base64Data);
      analyzeImage(base64Data);
    };
    reader.readAsDataURL(file);
  };

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(videoRef.current, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      setCapturedImage(dataUrl);
      stopCamera();
      analyzeImage(dataUrl);
    }
  };

  const analyzeImage = async (base64Data: string) => {
    setView('loading');
    
    try {
      // Call local ML backend instead of Google GenAI
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Data,
          language: 'hindi' // Can be changed to 'marathi'
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const apiResult = await response.json();

      if (apiResult.status === 'error') {
        alert(`Analysis failed: ${apiResult.message}`);
        setView('home');
        return;
      }

      if (apiResult.status === 'uncertain') {
        alert(`Uncertain: ${apiResult.message}\n\nPlease try with a clearer image.`);
        setView('home');
        return;
      }

      // Transform backend response to frontend format
      const recommendations = apiResult.recommendations;
      const data = {
        cropName: apiResult.cropName,
        diseaseName: apiResult.diseaseName,
        confidence: apiResult.confidence as 'High' | 'Medium' | 'Low',
        status: apiResult.healthStatus as 'Healthy' | 'Monitor' | 'Action',
        recommendations: {
          traditional: recommendations.Treatment || recommendations.Identification || [],
          bestPractices: [], // Will be populated from recommendations if available
          chemical: recommendations.Chemical || 'Not applicable',
          whatNotToDo: recommendations.Causes || []
        }
      };

      const newScan: ScanResult = {
        ...data,
        id: Date.now().toString(),
        timestamp: Date.now(),
        imageUrl: base64Data
      };

      setCurrentScan(newScan);
      setScans(prev => [newScan, ...prev]);
      setView('result');
    } catch (err) {
      console.error("Analysis Error:", err);
      alert("Failed to analyze. Make sure:\n1. Backend is running (python backend.py)\n2. You're on the right network");
      setView('home');
    }
  };

  // --- Views ---

  const HomeView = () => (
    <div className="flex-1 overflow-y-auto px-5 pt-8 pb-32 hide-scrollbar">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1B4332] mb-2">My Field</h1>
        <p className="text-[#748E81] text-lg font-medium">Monday, 12 Oct</p>
      </div>

      <Card className="mb-6 bg-gradient-to-br from-[#1B4332] to-[#2D6A4F] text-white border-none p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <span className="bg-[#ffffff20] px-3 py-1 rounded-full text-xs font-semibold mb-2 inline-block">PREMIUM CROP</span>
            <h2 className="text-2xl font-bold">Main Rice Field</h2>
          </div>
          <div className="bg-[#ffffff20] p-2 rounded-xl">
            <Leaf size={24} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Droplet size={18} className="opacity-70" />
            <span className="text-sm">Moist Soil</span>
          </div>
          <div className="flex items-center gap-2">
            <Sun size={18} className="opacity-70" />
            <span className="text-sm">Sunny</span>
          </div>
        </div>
      </Card>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-[#1B4332]">Recent Scans</h3>
          <button onClick={() => setView('history')} className="text-[#52B788] font-bold text-sm">See all</button>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-4 hide-scrollbar">
          {scans.length === 0 ? (
            <div className="w-full text-center py-10 text-[#748E81] border-2 border-dashed border-[#E9F5ED] rounded-3xl">
              No scans yet. Start by scanning a leaf.
            </div>
          ) : (
            scans.slice(0, 3).map(scan => (
              <Card key={scan.id} className="min-w-[160px] p-3" onClick={() => { setCurrentScan(scan); setView('result'); }}>
                <img src={scan.imageUrl} className="w-full h-24 object-cover rounded-2xl mb-2" />
                <p className="font-bold text-[#1B4332] text-sm truncate">{scan.cropName}</p>
                <p className="text-xs text-[#748E81]">{scan.diseaseName}</p>
              </Card>
            ))
          )}
        </div>
      </div>

      <Card className="mb-6 bg-[#D8F3DC] border-none p-5">
        <div className="flex items-center gap-4">
          <div className="bg-[#1B4332] text-white p-3 rounded-2xl">
            <Info size={24} />
          </div>
          <div>
            <p className="text-[#1B4332] font-bold">Farming Tip</p>
            <p className="text-sm text-[#2D6A4F]">Early detection can save up to 40% of your crop yield.</p>
          </div>
        </div>
      </Card>

      <div className="flex gap-3 mb-8">
        <button 
          onClick={() => fileInputRef.current?.click()}
          className="flex-1 bg-[#52B788] text-white py-3 px-4 rounded-2xl font-semibold hover:bg-[#2D6A4F] transition-all"
        >
          📁 Upload Image
        </button>
      </div>
      <input 
        type="file" 
        ref={fileInputRef}
        accept="image/*"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />

      {error && (
        <Card className="mb-6 bg-[#FFE9E9] border-none p-4">
          <p className="text-[#A30000] font-semibold">{error}</p>
        </Card>
      )}
    </div>
  );

  const ScanView = () => (
    <div className="flex-1 bg-black relative flex flex-col">
      <div className="absolute top-6 left-5 z-20">
        <button onClick={() => { stopCamera(); setView('home'); }} className="bg-white/20 backdrop-blur-md p-3 rounded-full text-white">
          <X size={24} />
        </button>
      </div>

      <video 
        ref={videoRef} 
        autoPlay 
        playsInline 
        className="flex-1 object-cover"
      />

      <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-10">
        <div className="w-full aspect-[3/4] border-2 border-dashed border-white/50 rounded-3xl relative">
          <div className="absolute top-[-2px] left-[-2px] w-10 h-10 border-t-4 border-l-4 border-white rounded-tl-xl"></div>
          <div className="absolute top-[-2px] right-[-2px] w-10 h-10 border-t-4 border-r-4 border-white rounded-tr-xl"></div>
          <div className="absolute bottom-[-2px] left-[-2px] w-10 h-10 border-b-4 border-l-4 border-white rounded-bl-xl"></div>
          <div className="absolute bottom-[-2px] right-[-2px] w-10 h-10 border-b-4 border-r-4 border-white rounded-br-xl"></div>
          <p className="absolute bottom-[-40px] left-0 right-0 text-center text-white text-sm font-medium">Place leaf inside frame</p>
        </div>
      </div>

      <div className="bg-gradient-to-t from-black/80 to-transparent p-10 flex flex-col items-center">
        <div className="flex gap-4 mb-8">
           <div className="flex items-center gap-2 bg-white/10 backdrop-blur px-4 py-2 rounded-full text-white text-sm">
             <Sun size={14} /> Natural Light
           </div>
           <div className="flex items-center gap-2 bg-white/10 backdrop-blur px-4 py-2 rounded-full text-white text-sm">
             <AlertCircle size={14} /> One Leaf
           </div>
        </div>
        <div className="flex gap-4 items-center">
          <button 
            onClick={capturePhoto}
            className="w-20 h-20 rounded-full border-4 border-white flex items-center justify-center bg-white/20 active:scale-95 transition-transform"
          >
            <div className="w-16 h-16 rounded-full bg-white"></div>
          </button>
          <p className="text-white text-sm">or</p>
          <button 
            onClick={() => { stopCamera(); fileInputRef.current?.click(); }}
            className="px-6 py-3 bg-white/20 text-white rounded-full border-2 border-white/50 font-semibold hover:bg-white/30 transition-all"
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );

  const LoadingView = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-10 text-center">
      <div className="relative mb-10">
        <div className="w-32 h-32 bg-[#D8F3DC] rounded-full flex items-center justify-center animate-pulse-soft">
          <Leaf size={60} className="text-[#1B4332]" />
        </div>
        <div className="absolute inset-0 border-4 border-dashed border-[#1B4332] rounded-full animate-[spin_10s_linear_infinite] opacity-30"></div>
      </div>
      
      <h2 className="text-2xl font-bold text-[#1B4332] mb-4">Analyzing Leaf...</h2>
      <div className="space-y-3">
        <p className="text-[#748E81] flex items-center gap-3 justify-center">
          <CheckCircle2 size={16} className="text-[#52B788]" /> Identifying crop type
        </p>
        <p className="text-[#748E81] flex items-center gap-3 justify-center">
          <CheckCircle2 size={16} className="text-[#52B788]" /> Scanning for disease
        </p>
        <p className="text-[#748E81] flex items-center gap-3 justify-center">
          <RefreshCcw size={16} className="animate-spin text-[#1B4332]" /> Checking treatments
        </p>
      </div>
      
      <p className="mt-12 text-sm text-[#748E81] italic font-medium">"Healthy fields are the backbone of a strong family."</p>
    </div>
  );

  const ResultView = () => {
    if (!currentScan) return null;

    const statusColors = {
      Healthy: { bg: 'bg-[#D8F3DC]', text: 'text-[#1B4332]', icon: CheckCircle2, banner: '✅ No action needed now' },
      Monitor: { bg: 'bg-[#FFFBEC]', text: 'text-[#947600]', icon: Info, banner: '🟡 Monitor & use local practices' },
      Action: { bg: 'bg-[#FFE9E9]', text: 'text-[#A30000]', icon: AlertCircle, banner: '🔴 Immediate attention required' }
    };

    const config = statusColors[currentScan.status];

    return (
      <div className="flex-1 overflow-y-auto hide-scrollbar">
        <div className="relative h-64">
          <img src={currentScan.imageUrl} className="w-full h-full object-cover" />
          <button 
            onClick={() => setView('home')} 
            className="absolute top-6 left-5 bg-black/30 backdrop-blur p-3 rounded-full text-white"
          >
            <ArrowLeft size={24} />
          </button>
        </div>

        <div className="bg-white -mt-8 rounded-t-[40px] px-6 pt-8 pb-32">
          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Leaf size={18} className="text-[#52B788]" />
                <span className="text-[#748E81] font-bold text-sm uppercase tracking-wide">Crop Identified</span>
              </div>
              <h2 className="text-3xl font-bold text-[#1B4332]">{currentScan.cropName}</h2>
            </div>
            <div className="text-right">
              <span className={`px-4 py-1.5 rounded-full text-xs font-bold ${config.bg} ${config.text}`}>
                {currentScan.confidence} Confidence
              </span>
            </div>
          </div>

          <div className={`flex items-center gap-4 ${config.bg} ${config.text} p-4 rounded-2xl mb-8`}>
            <config.icon size={28} />
            <div>
              <p className="font-bold text-lg">{currentScan.diseaseName}</p>
              <p className="text-sm font-medium">{config.banner}</p>
            </div>
          </div>

          <div className="space-y-8">
            <section>
              <h3 className="text-xl font-bold text-[#1B4332] mb-4 flex items-center gap-2">
                <span className="w-2 h-8 bg-[#52B788] rounded-full"></span>
                Local Recommendations
              </h3>
              <div className="space-y-4">
                {currentScan.recommendations.traditional.map((item, i) => (
                  <div key={i} className="flex gap-4 items-start bg-[#F0FFF4] p-4 rounded-2xl">
                    <div className="bg-[#1B4332] text-white p-2 rounded-xl mt-0.5">
                      <Zap size={16} />
                    </div>
                    <p className="text-[#2D6A4F] font-medium leading-relaxed">{item}</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xl font-bold text-[#1B4332] mb-4 flex items-center gap-2">
                <span className="w-2 h-8 bg-[#748E81] rounded-full"></span>
                Good Practices
              </h3>
              <ul className="space-y-3">
                {currentScan.recommendations.bestPractices.map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-[#52796F] font-medium">
                    <div className="w-2 h-2 rounded-full bg-[#52B788]"></div>
                    {item}
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-[#FFF8E1] p-6 rounded-3xl">
               <h3 className="font-bold text-[#856404] mb-2 flex items-center gap-2">
                 <AlertCircle size={18} /> Chemical Advice
               </h3>
               <p className="text-[#856404] text-sm leading-relaxed mb-4">
                 {currentScan.recommendations.chemical}
               </p>
               <div className="p-3 bg-white/50 rounded-xl">
                 <p className="text-xs font-bold text-[#856404] uppercase mb-2 tracking-tight">❌ What NOT to do</p>
                 <ul className="space-y-1">
                   {currentScan.recommendations.whatNotToDo.map((item, i) => (
                     <li key={i} className="text-xs text-[#856404]">• {item}</li>
                   ))}
                 </ul>
               </div>
            </section>
          </div>

          <div className="mt-12 text-center border-t border-[#E9F5ED] pt-8">
            <p className="text-xs text-[#748E81] leading-relaxed">
              This advice is based on image analysis and common farming practices. 
              For severe cases, please consult a local agriculture expert.
            </p>
          </div>
        </div>
      </div>
    );
  };

  const HistoryView = () => (
    <div className="flex-1 overflow-y-auto px-5 pt-8 pb-32 hide-scrollbar">
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => setView('home')} className="bg-[#F0FFF4] p-2 rounded-xl text-[#1B4332]">
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-3xl font-bold text-[#1B4332]">History</h1>
      </div>

      <div className="space-y-4">
        {scans.length === 0 ? (
          <div className="text-center py-20 text-[#748E81]">
            No scans recorded yet.
          </div>
        ) : (
          scans.map(scan => (
            <Card key={scan.id} className="flex gap-4 items-center" onClick={() => { setCurrentScan(scan); setView('result'); }}>
              <img src={scan.imageUrl} className="w-20 h-20 object-cover rounded-2xl" />
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-[#1B4332]">{scan.cropName}</h4>
                  <span className="text-[10px] text-[#748E81] font-bold uppercase">{new Date(scan.timestamp).toLocaleDateString()}</span>
                </div>
                <p className="text-sm text-[#748E81] mb-1">{scan.diseaseName}</p>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${scan.status === 'Healthy' ? 'bg-[#D8F3DC] text-[#1B4332]' : 'bg-[#FFFBEC] text-[#947600]'}`}>
                  {scan.status}
                </span>
              </div>
              <ChevronRight size={20} className="text-[#E9F5ED]" />
            </Card>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="h-full w-full flex flex-col bg-[#F7FBF8]">
      {/* Top Bar - Branding */}
      {view !== 'scan' && view !== 'loading' && (
        <div className="px-5 py-4 flex justify-between items-center bg-white z-10">
          <div className="flex items-center gap-2">
            <div className="bg-[#1B4332] p-1.5 rounded-lg">
              <Leaf size={18} className="text-white" />
            </div>
            <span className="text-xl font-black text-[#1B4332] tracking-tight">KisanSeva</span>
          </div>
          <button className="w-10 h-10 bg-[#F0FFF4] rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-[#52B788] rounded-full"></div>
          </button>
        </div>
      )}

      {/* Main Content Area */}
      {view === 'home' && <HomeView />}
      {view === 'scan' && <ScanView />}
      {view === 'loading' && <LoadingView />}
      {view === 'result' && <ResultView />}
      {view === 'history' && <HistoryView />}

      {/* Bottom Navigation */}
      {view !== 'scan' && view !== 'loading' && (
        <div className="absolute bottom-0 left-0 right-0 p-5 z-20 pointer-events-none">
          <div className="max-w-md mx-auto bg-white rounded-[32px] shadow-[0_-10px_30px_rgba(27,67,50,0.08)] flex justify-between items-center px-4 py-3 border border-[#E9F5ED] pointer-events-auto">
            <button 
              onClick={() => setView('home')}
              className={`flex flex-col items-center gap-1 p-2 rounded-2xl flex-1 ${view === 'home' ? 'text-[#1B4332]' : 'text-[#748E81]'}`}
            >
              <Home size={24} fill={view === 'home' ? '#1B4332' : 'none'} />
              <span className="text-[10px] font-bold">Home</span>
            </button>
            
            <button 
              onClick={startCamera}
              className="bg-[#1B4332] text-white w-14 h-14 rounded-full flex items-center justify-center -mt-12 shadow-lg shadow-[#1B4332]/30 active:scale-90 transition-transform"
            >
              <Camera size={28} />
            </button>

            <button 
              onClick={() => setView('history')}
              className={`flex flex-col items-center gap-1 p-2 rounded-2xl flex-1 ${view === 'history' ? 'text-[#1B4332]' : 'text-[#748E81]'}`}
            >
              <History size={24} />
              <span className="text-[10px] font-bold">History</span>
            </button>
          </div>
          <div className="h-4 safe-bottom"></div>
        </div>
      )}
    </div>
  );
};

createRoot(document.getElementById('root')!).render(<App />);
