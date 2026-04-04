"use client";
import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import { 
  Send, Mic, MicOff, Square, Loader2, CheckCircle2, 
  ArrowLeft, AlertTriangle, Volume2
} from "lucide-react";
import Navbar from "@/components/Navbar";

const API_BASE = "/api";

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Live Session Page
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params.agentId;

  const [agent, setAgent] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [collectedFields, setCollectedFields] = useState({});
  const [missingFields, setMissingFields] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const [ending, setEnding] = useState(false);

  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Start session on mount
  useEffect(() => {
    if (agentId) startSession();
  }, [agentId]);

  const startSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to start session");
      }
      const data = await res.json();
      setAgent(data.agent);
      setSessionId(data.session_id);
      setMissingFields(data.missing_fields || []);
      setMessages([{ role: "assistant", content: data.greeting }]);
    } catch (err) {
      setError(`Failed to start session: ${err.message}. Make sure the backend is running on port 8000.`);
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim() || !sessionId || sending) return;

    const userMsg = { role: "user", content: text.trim() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text.trim(), input_type: "text" }),
      });
      if (!res.ok) throw new Error("Send failed");
      const data = await res.json();

      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
      setCollectedFields(data.collected_fields || {});
      setMissingFields(data.missing_fields || []);
      setIsComplete(data.is_complete || false);

      if (data.is_escalation) {
        setMessages(prev => [...prev, { 
          role: "system", 
          content: "⚠️ Escalation triggered — connecting to human agent." 
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: "system", 
        content: "Failed to get response. Please try again." 
      }]);
    } finally {
      setSending(false);
    }
  };

  // ── Voice Recording ─────────────────────────────────────────
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await transcribeAndSend(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError("Microphone access denied. Please allow microphone access in your browser settings.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAndSend = async (audioBlob) => {
    setSending(true);
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      const res = await fetch(`${API_BASE}/transcribe`, { method: "POST", body: formData });
      if (!res.ok) throw new Error("Transcription failed");

      const data = await res.json();
      if (data.transcript) {
        await sendMessage(data.transcript);
      } else {
        setError("Could not transcribe audio. Please try again or type your message.");
      }
    } catch (err) {
      setError("Voice transcription failed. The ASR service may not be configured. Please type your message instead.");
      setSending(false);
    }
  };

  // ── End Session ─────────────────────────────────────────────
  const endSession = async () => {
    if (!sessionId) return;
    setEnding(true);
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}/end`, { method: "POST" });
      router.push(`/session/${agentId}/stats?sid=${sessionId}`);
    } catch (err) {
      setError("Failed to end session.");
      setEnding(false);
    }
  };

  // ── Loading / Error States ──────────────────────────────────
  if (error && !sessionId) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-32 px-6 max-w-2xl mx-auto text-center space-y-8">
          <AlertTriangle size={48} className="text-saffron mx-auto" />
          <h2 className="text-3xl font-display text-white">Connection Error</h2>
          <p className="text-muted leading-relaxed">{error}</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => router.push("/build")} className="px-6 py-3 border border-white/10 rounded-full text-sm hover:bg-white/5 transition-all">
              Back to Build
            </button>
            <button onClick={() => { setError(null); startSession(); }} className="btn-primary px-6 py-3 rounded-full text-sm">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Navbar />
        <Loader2 size={32} className="text-saffron animate-spin" />
      </div>
    );
  }

  const voiceEnabled = agent.inputs?.includes("Voice");
  const fieldProgress = agent.fields?.length 
    ? Math.round((Object.keys(collectedFields).length / agent.fields.length) * 100) 
    : 0;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <div className="noise-overlay" />

      {/* Main Content */}
      <div className="flex-1 flex pt-20">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4">
          {/* Session Header */}
          <div className="py-6 flex items-center justify-between border-b border-white/5">
            <div className="flex items-center gap-4">
              <button onClick={() => router.push("/build")} className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition-all">
                <ArrowLeft size={18} />
              </button>
              <div>
                <h2 className="text-xl font-display text-white">{agent.name}</h2>
                <span className="text-[10px] font-mono text-saffron uppercase tracking-widest">{agent.domain === "Others" ? agent.customDomain : agent.domain}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {isComplete && (
                <span className="flex items-center gap-2 text-emerald-500 text-xs font-mono uppercase tracking-widest">
                  <CheckCircle2 size={14} /> Complete
                </span>
              )}
              <button
                onClick={endSession}
                disabled={ending}
                className="px-5 py-2 rounded-full border border-saffron/40 text-saffron text-xs font-mono uppercase tracking-widest hover:bg-saffron/10 transition-all disabled:opacity-50"
              >
                {ending ? "Ending..." : "End Session"}
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto py-8 space-y-6">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "system" ? (
                  <div className="bg-saffron/10 border border-saffron/20 rounded-2xl px-5 py-3 max-w-lg">
                    <p className="text-sm text-saffron">{msg.content}</p>
                  </div>
                ) : (
                  <div className={`max-w-[75%] rounded-3xl px-6 py-4 ${
                    msg.role === "user" 
                      ? "bg-saffron/15 border border-saffron/20 text-white" 
                      : "bg-white/[0.04] border border-white/10 text-white"
                  }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    <span className={`text-[9px] font-mono uppercase tracking-widest mt-2 block ${
                      msg.role === "user" ? "text-saffron/60 text-right" : "text-muted"
                    }`}>
                      {msg.role === "user" ? "You" : agent.name}
                    </span>
                  </div>
                )}
              </motion.div>
            ))}

            {sending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-white/[0.04] border border-white/10 rounded-3xl px-6 py-4 flex items-center gap-3">
                  <div className="flex gap-1">
                    {[0, 1, 2].map(i => (
                      <div key={i} className="w-2 h-2 rounded-full bg-saffron/50 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                  <span className="text-[10px] font-mono text-muted">Thinking...</span>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="pb-6 pt-4 border-t border-white/5">
            {error && (
              <div className="mb-3 bg-saffron/10 border border-saffron/20 rounded-xl px-4 py-2 flex items-center justify-between">
                <p className="text-xs text-saffron">{error}</p>
                <button onClick={() => setError(null)} className="text-saffron hover:text-white">✕</button>
              </div>
            )}
            <div className="flex items-center gap-3">
              {voiceEnabled && (
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={sending}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                    isRecording 
                      ? "bg-red-500/20 border-2 border-red-500 text-red-400 animate-pulse" 
                      : "bg-white/5 border border-white/10 text-muted hover:text-saffron hover:border-saffron/30"
                  } disabled:opacity-50`}
                >
                  {isRecording ? <Square size={18} /> : <Mic size={18} />}
                </button>
              )}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }}
                placeholder={isRecording ? "Recording... click stop to send" : "Type your message..."}
                disabled={sending || isRecording}
                className="flex-1 bg-white/[0.03] border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-saffron/40 transition-all disabled:opacity-50 placeholder:text-muted/50"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || sending}
                className="w-12 h-12 rounded-full bg-saffron flex items-center justify-center text-black hover:scale-105 active:scale-95 transition-all disabled:opacity-30 disabled:hover:scale-100"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar — Field Tracker */}
        <div className="hidden lg:block w-80 border-l border-white/5 p-6 overflow-y-auto">
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-4">Collection Progress</h3>
              <div className="w-full bg-white/5 rounded-full h-2 mb-2">
                <motion.div 
                  className="bg-saffron rounded-full h-2" 
                  initial={{ width: 0 }}
                  animate={{ width: `${fieldProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <span className="text-[10px] font-mono text-muted">{fieldProgress}% complete</span>
            </div>

            {/* Collected Fields */}
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Collected</h3>
              <div className="space-y-2">
                {Object.entries(collectedFields).map(([key, val]) => (
                  <div key={key} className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3">
                    <span className="text-[10px] font-mono text-emerald-500 uppercase tracking-widest block">{key}</span>
                    <span className="text-xs text-white mt-1 block">{String(val)}</span>
                  </div>
                ))}
                {Object.keys(collectedFields).length === 0 && (
                  <p className="text-[10px] font-mono text-muted italic">No fields collected yet</p>
                )}
              </div>
            </div>

            {/* Missing Fields */}
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Pending</h3>
              <div className="space-y-1.5">
                {missingFields.map((f) => (
                  <div key={f} className="bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2">
                    <span className="text-[10px] font-mono text-muted">{f}</span>
                  </div>
                ))}
                {missingFields.length === 0 && (
                  <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3 text-center">
                    <CheckCircle2 size={20} className="text-emerald-500 mx-auto mb-1" />
                    <span className="text-[10px] font-mono text-emerald-500">All fields collected!</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
