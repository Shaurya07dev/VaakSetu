"use client";
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Upload, FileAudio, Users, Loader2, CheckCircle2, 
  AlertTriangle, Network, ListChecks, PlayCircle 
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";

// Since it's a long running operation, we use API_DIRECT.
const API_DIRECT = typeof window !== "undefined"
  ? `http://${window.location.hostname}:8000/api`
  : "http://localhost:8000/api";

export default function AnalysisPage() {
  const router = useRouter();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  
  const [file, setFile] = useState(null);
  const [numSpeakers, setNumSpeakers] = useState(2);
  const [isDragging, setIsDragging] = useState(false);
  
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  // Load agents
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch("/api/agents");
        if (res.ok) {
          const data = await res.json();
          setAgents(data);
          if (data.length > 0) setSelectedAgent(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load agents", err);
      }
    };
    fetchAgents();
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!file || !selectedAgent) return;
    
    setAnalyzing(true);
    setError(null);
    setResult(null);
    
    try {
      const formData = new FormData();
      formData.append("audio", file);
      formData.append("agent_id", selectedAgent);
      formData.append("num_speakers", numSpeakers.toString());
      
      const res = await fetch(`${API_DIRECT}/analyze-conversation`, {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Analysis failed");
      }
      
      const data = await res.json();
      setResult(data.data);
    } catch (err) {
      setError(err.message || "An unexpected error occurred. Note: requires HF_TOKEN setup on backend.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <div className="noise-overlay" />

      <main className="flex-1 pt-24 px-6 pb-12 max-w-6xl mx-auto w-full relative z-10 flex flex-col md:flex-row gap-8">
        
        {/* Left Column - Form & Controls */}
        <div className="w-full md:w-1/3 flex flex-col gap-6">
          <div>
            <h1 className="text-3xl font-display text-white mb-2">Voice Bifurcation</h1>
            <p className="text-muted text-sm leading-relaxed">
              Upload a multi-speaker audio recording. The system will separate speakers, transcribe the dialog, and generate structured insights.
            </p>
          </div>
          
          {/* Form Card */}
          <div className="p-6 bg-white/[0.02] border border-white/10 rounded-2xl flex flex-col gap-5">
            {/* Agent Select */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-mono text-saffron uppercase tracking-widest">Base Agent Template</label>
              <select 
                value={selectedAgent || ""}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-saffron/50 transition-all appearance-none"
              >
                {agents.map(a => (
                  <option key={a.id} value={a.id} className="bg-[#121212]">{a.name} ({a.domain})</option>
                ))}
              </select>
            </div>
            
            {/* Speakers Selector */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-mono text-white/50 uppercase tracking-widest flex items-center justify-between">
                <span>Number of Speakers</span>
                <span>{numSpeakers}</span>
              </label>
              <input 
                type="range" 
                min="2" max="5" 
                value={numSpeakers}
                onChange={(e) => setNumSpeakers(parseInt(e.target.value))}
                className="accent-saffron"
              />
            </div>
            
            {/* File Upload Zone */}
            <div 
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('audio-upload')?.click()}
              className={`mt-2 border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                isDragging ? "border-saffron bg-saffron/5 text-saffron" 
                : file ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-500"
                : "border-white/10 hover:border-white/20 text-muted"
              }`}
            >
              <input 
                type="file" 
                id="audio-upload" 
                className="hidden" 
                accept="audio/*" 
                onChange={handleFileChange}
              />
              {file ? (
                <>
                  <FileAudio size={32} className="mb-3" />
                  <p className="text-sm font-medium text-white">{file.name}</p>
                  <p className="text-xs opacity-70 mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </>
              ) : (
                <>
                  <Upload size={32} className="mb-3 opacity-50" />
                  <p className="text-sm">Drag audio file here or <span className="text-saffron">browse</span></p>
                  <p className="text-xs opacity-50 mt-1">WAV, MP3, M4A supported</p>
                </>
              )}
            </div>
            
            <button 
              onClick={startAnalysis}
              disabled={!file || !selectedAgent || analyzing}
              className="btn-primary w-full py-4 rounded-xl flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
            >
              {analyzing ? (
                <><Loader2 size={16} className="animate-spin" /> Abstracting Insights...</>
              ) : (
                <><Network size={16} /> Analyze Conversation</>
              )}
            </button>
            
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 flex gap-2 text-red-400">
                <AlertTriangle size={16} className="shrink-0 mt-0.5" />
                <p className="text-xs leading-relaxed">{error}</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Right Column - Results */}
        <div className="w-full md:w-2/3 flex flex-col h-[calc(100vh-8rem)]">
          {!result && !analyzing ? (
            <div className="flex-1 border border-white/5 bg-white/[0.01] rounded-2xl flex flex-col items-center justify-center text-center p-12 overflow-hidden relative">
              <div className="absolute inset-0 bg-saffron/5 blur-3xl rounded-full opacity-20 scale-150 -z-10" />
              <Network size={64} strokeWidth={1} className="text-white/10 mb-6" />
              <h3 className="text-xl text-white/50 font-display">Awaiting Audio Processing</h3>
              <p className="text-muted/50 text-sm mt-3 max-w-sm">
                Upload a conversation to see AI-generated diarization, full transcriptions, and structured metadata extraction.
              </p>
            </div>
          ) : analyzing ? (
            <div className="flex-1 border border-white/5 bg-white/[0.01] rounded-2xl flex flex-col items-center justify-center text-center p-12">
              <Loader2 size={48} className="text-saffron animate-spin mb-6" />
              <h3 className="text-xl text-white font-display mb-2">Analyzing Audio Signals...</h3>
              <p className="text-muted text-sm max-w-sm">
                This process involves Speaker Diarization, localized transcribing via Sarvam STT, and contextual LLM extraction. This may take a minute.
              </p>
              
              <div className="w-64 bg-white/5 rounded-full h-1 mt-8 overflow-hidden">
                <div className="h-full bg-saffron w-1/3 animate-pulse rounded-full" />
              </div>
            </div>
          ) : (
            <motion.div 
              initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}}
              className="flex-1 flex flex-col min-h-0"
            >
              {/* Insight Cards Overview */}
              <div className="grid grid-cols-2 gap-4 mb-6 shrink-0">
                <div className="bg-gradient-to-br from-saffron/20 to-saffron/5 border border-saffron/20 rounded-2xl p-5">
                  <h4 className="text-xs font-mono text-saffron uppercase tracking-widest mb-1 flex items-center gap-2">
                    <ListChecks size={14} /> AI Summary
                  </h4>
                  <p className="text-white text-sm leading-relaxed mt-3">{result.summary}</p>
                </div>
                
                <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-5 flex flex-col">
                  <h4 className="text-xs font-mono text-white/50 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <CheckCircle2 size={14} /> Extracted Data
                  </h4>
                  <div className="flex-1 overflow-y-auto pr-2 space-y-2">
                    {Object.keys(result.analysis || {}).length === 0 ? (
                      <span className="text-muted text-xs italic">No relevant configuration fields matched.</span>
                    ) : null}
                    {Object.entries(result.analysis || {}).map(([key, val]) => (
                      <div key={key} className="flex justify-between items-start border-b border-white/5 pb-2">
                        <span className="text-xs text-muted">{key}</span>
                        <span className="text-xs text-white max-w-[60%] text-right font-medium">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Diarization Timeline */}
              <div className="flex-1 bg-white/[0.02] border border-white/10 rounded-2xl overflow-y-auto p-6 scrollbar-thin flex flex-col min-h-0">
                <h4 className="text-xs font-mono text-white/50 uppercase tracking-widest mb-6 sticky top-0 bg-[#0A0A0A] pb-2 z-10 border-b border-white/5">
                  Transcription Timeline
                </h4>
                
                <div className="space-y-6">
                  {result.segments?.map((seg, idx) => (
                    <div key={idx} className="flex gap-4">
                      {/* Timeline graphic */}
                      <div className="flex flex-col items-center shrink-0">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border ${strToColorProps(seg.speaker)}`}>
                          {seg.speaker.replace("SPEAKER_", "S")}
                        </div>
                        {idx !== result.segments.length - 1 && (
                          <div className="w-px h-full bg-white/5 mt-2 min-h-[1.5rem]" />
                        )}
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 pb-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-white">{seg.speaker}</span>
                          <span className="text-[10px] text-muted font-mono">{formatTime(seg.start)} - {formatTime(seg.end)}</span>
                        </div>
                        <p className="text-sm text-white/80 leading-relaxed bg-white/[0.02] inline-block px-4 py-2 rounded-xl mt-1">
                          {seg.transcript}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {(!result.segments || result.segments.length === 0) && (
                    <div className="text-center py-8 text-muted text-sm">
                      No voices detected in the audio.
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

// Helpers
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// Generate consistent colors for different speakers
function strToColorProps(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
  const colors = [
    "bg-blue-500/10 border-blue-500/30 text-blue-400",
    "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
    "bg-purple-500/10 border-purple-500/30 text-purple-400",
    "bg-orange-500/10 border-orange-500/30 text-orange-400",
    "bg-pink-500/10 border-pink-500/30 text-pink-400",
  ];
  return colors[Math.abs(hash) % colors.length];
}
