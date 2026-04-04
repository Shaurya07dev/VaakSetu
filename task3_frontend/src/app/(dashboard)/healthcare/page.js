"use client";
import React from "react";
import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
const fadeUp = {
  initial: { opacity: 0, y: 30, filter: "blur(10px)" },
  whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
  transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  viewport: { once: true }
};
import ScrollReveal from "@/components/ScrollReveal";
export default function HealthcarePage() {
  return (
    <div className="relative pt-32 pb-40 px-6">
      <Navbar />
      <div className="noise-overlay" />
      <section className="max-w-7xl mx-auto space-y-24">
        {/* Header */}
        <ScrollReveal width="100%">
          <motion.div {...fadeUp} className="max-w-4xl">
            <span className="text-cyan-vivid font-mono text-xs uppercase tracking-widest mb-6 inline-block">Primary System — Vertical 01</span>
            <h1 className="text-fluid-h1 mb-8">Healthcare & <span className="italic font-display opacity-80">Emergency AI</span></h1>
            <p className="text-xl text-muted leading-relaxed max-w-2xl">
              A voice-based triage assistant that listens to patients, understands symptoms in multilingual/code-mixed speech, and generates structured medical records in real time.
            </p>
          </motion.div>
        </ScrollReveal>
        {/* Live Simulation Card */}
        <ScrollReveal width="100%" delay={0.2}>
          <motion.div 
            {...fadeUp}
            className="glass-card p-1 md:p-1 overflow-hidden bg-cyan-vivid/5 border-cyan-vivid/20"
          >
            <div className="grid md:grid-cols-2">
              <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-cyan-vivid/20 space-y-8">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-2 h-2 rounded-full bg-cyan-vivid animate-pulse" />
                  <span className="text-xs font-mono uppercase tracking-widest text-cyan-vivid">Voice Stream Active</span>
                </div>
                <div className="space-y-6">
                  <div className="bg-background/40 p-5 rounded-2xl border border-border/50 max-w-[80%]">
                      <p className="text-sm italic">&ldquo;Mujhe 3 din se bukhar hai aur sir dard bhi ho raha hai...&rdquo;</p>
                      <p className="text-[10px] uppercase font-mono mt-2 text-muted tracking-widest">Detected: Hindi + English</p>
                  </div>
                  <div className="bg-cyan-vivid/10 p-5 rounded-2xl border border-cyan-vivid/30 max-w-[80%] ml-auto text-right">
                      <p className="text-sm font-medium">&ldquo;Aapko bukhar kitna hai? Kya aapne koi dawa li hai?&rdquo;</p>
                      <p className="text-[10px] uppercase font-mono mt-2 text-cyan-vivid tracking-widest">AI Action: Follow-up Insight</p>
                  </div>
                </div>
                <div className="pt-8 border-t border-cyan-vivid/10">
                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      {[1, 2, 3].map(i => <div key={i} className="w-1.5 h-1.5 rounded-full bg-cyan-vivid/40 h-8 md:h-12 w-1 animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />)}
                    </div>
                    <button className="px-6 py-2 rounded-full border border-cyan-vivid/40 bg-cyan-vivid/10 text-xs font-mono uppercase tracking-widest text-cyan-vivid">
                        Stop Session
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-8 md:p-12 space-y-8 bg-background/30 backdrop-blur-3xl">
                <span className="text-xs font-mono uppercase tracking-widest text-muted">Structured Analysis</span>
                <div className="space-y-4">
                  {[
                    { label: "Symptoms", value: "Fever, Headache", color: "text-cyan-vivid" },
                    { label: "Duration", value: "3 Days", color: "text-foreground" },
                    { label: "Medications", value: "Paracetamol (Ineffective)", color: "text-foreground" },
                    { label: "Risk Level", value: "Moderate / Urgent", color: "text-saffron" },
                  ].map((item, i) => (
                    <div key={i} className="flex justify-between items-center py-3 border-b border-border/40">
                      <span className="text-[10px] uppercase font-mono tracking-widest text-muted">{item.label}</span>
                      <span className={`text-sm font-semibold tracking-tight ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
                <div className="p-5 rounded-2xl border border-saffron/20 bg-saffron/5">
                  <p className="text-[10px] uppercase font-mono mb-2 text-saffron tracking-widest">Automatic Escalation</p>
                  <p className="text-xs text-muted leading-relaxed">System detected panic keywords and prolonged high-fever indicators. Hospital dashboard alerted via Webhook.</p>
                </div>
              </div>
            </div>
          </motion.div>
        </ScrollReveal>
        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { title: "Conversation Intake", desc: "No manual forms. Just natural speech in 11+ languages including code-mixed Hinglish." },
            { title: "Medical Record Auto-fill", desc: "Converts messy speech into structured fields: symptoms, history, risk indicators." },
            { title: "Emergency Triage", desc: "Real-time risk scoring using clinical protocols. Alerts sent to hospital triage pods." },
          ].map((feature, i) => (
            <ScrollReveal key={i} delay={i * 0.1}>
              <motion.div {...fadeUp} transition={{ delay: i * 0.2 }} className="glass-card p-10 border border-border/50 h-full">
                <h3 className="text-2xl mb-4 font-display">{feature.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{feature.desc}</p>
              </motion.div>
            </ScrollReveal>
          ))}
        </div>
      </section>
    </div>
  );
}
