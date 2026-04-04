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
export default function BankingPage() {
  return (
    <div className="relative pt-32 pb-40 px-6">
      <Navbar />
      <div className="noise-overlay" />
      <section className="max-w-7xl mx-auto space-y-24">
        {/* Header */}
        <ScrollReveal width="100%">
          <motion.div {...fadeUp} className="max-w-4xl">
            <span className="text-saffron font-mono text-xs uppercase tracking-widest mb-6 inline-block">Financial Operations — Vertical 02</span>
            <h1 className="text-fluid-h1 mb-8">Loan & <span className="italic font-display opacity-80">Debt Automation</span></h1>
            <p className="text-xl text-muted leading-relaxed max-w-2xl">
              A voice automation layer for financial institutions. Replacing thousands of manual manual follow-up calls with intelligent Agents that understand intent and collect structured records.
            </p>
          </motion.div>
        </ScrollReveal>
        {/* Call Flow Interface */}
        <ScrollReveal width="100%" delay={0.2}>
          <motion.div 
            {...fadeUp}
            className="glass-card p-1 overflow-hidden bg-saffron/5 border-saffron/20"
          >
            <div className="grid md:grid-cols-2 h-full">
              <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-saffron/20 space-y-8 bg-background/20">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-2 h-2 rounded-full bg-saffron animate-ping" />
                  <span className="text-xs font-mono uppercase tracking-widest text-saffron">Outbound Call Sequence</span>
                </div>
                <div className="space-y-6">
                  <div className="bg-saffron/10 p-5 rounded-2xl border border-saffron/30 max-w-[85%]">
                      <p className="text-sm font-medium">&ldquo;Namaste Ramesh ji, main bank se bol raha hoon. Aapka loan payment pending hai...&rdquo;</p>
                      <p className="text-[10px] uppercase font-mono mt-2 text-saffron tracking-widest">AI Action: Initiating Collection</p>
                  </div>
                  <div className="bg-background/40 p-5 rounded-2xl border border-border/50 max-w-[85%] ml-auto text-right">
                      <p className="text-sm italic">&ldquo;Haan bhai, abhi thoda problem chal raha hai, next week kar dunga payment.&rdquo;</p>
                      <p className="text-[10px] uppercase font-mono mt-2 text-muted tracking-widest">Detected: Negative / Postponed</p>
                  </div>
                  <div className="bg-saffron/10 p-5 rounded-2xl border border-saffron/30 max-w-[85%]">
                      <p className="text-sm font-medium">&ldquo;Aap exact date bata sakte hain? Aur payment kis method se karenge?&rdquo;</p>
                      <p className="text-[10px] uppercase font-mono mt-2 text-saffron tracking-widest">AI Action: Refining Intent</p>
                  </div>
                </div>
              </div>
              <div className="p-8 md:p-12 space-y-8 bg-background/30 backdrop-blur-3xl flex flex-col justify-between">
                <div>
                  <span className="text-xs font-mono uppercase tracking-widest text-muted">Intent Extraction</span>
                  <div className="space-y-4 mt-8">
                    {[
                      { label: "Payment Status", value: "Pending / Pushed", color: "text-saffron" },
                      { label: "Reason Code", value: "Financial Constraint", color: "text-foreground" },
                      { label: "Expected Date", value: "Next Week (May 12th)", color: "text-foreground" },
                      { label: "Confidence", value: "0.94 / Audit Green", color: "text-emerald-deep" },
                    ].map((item, i) => (
                      <div key={i} className="flex justify-between items-center py-3 border-b border-border/40">
                        <span className="text-[10px] uppercase font-mono tracking-widest text-muted">{item.label}</span>
                        <span className={`text-sm font-semibold tracking-tight ${item.color}`}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pt-8 border-t border-border/10">
                  <button className="w-full py-4 rounded-xl border border-saffron text-saffron font-bold text-xs uppercase tracking-widest hover:bg-saffron hover:text-black transition-all">
                      Generate Compliance Audit Log
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </ScrollReveal>
        {/* Efficiency Section */}
        <div className="grid md:grid-cols-2 gap-20 items-center">
            <ScrollReveal>
              <div className="space-y-6">
                  <h2 className="text-4xl text-foreground">Compliance-First <br/> Call Infrastructure</h2>
                  <p className="text-muted text-sm leading-relaxed">
                    Every interaction is logged with precise timestamps and confidence scoring. 
                    Audit logs are generated in real-time for regulatory compliance (RBI guidelines supported).
                  </p>
              </div>
            </ScrollReveal>
            <ScrollReveal delay={0.2}>
              <div className="glass-card p-10 bg-emerald-deep/5 border-emerald-deep/20 space-y-4 h-full">
                  <div className="text-5xl font-display text-emerald-deep">84%</div>
                  <p className="text-xs font-mono uppercase tracking-widest text-muted">Cost reduction vs Manual Call Centers</p>
              </div>
            </ScrollReveal>
        </div>
      </section>
    </div>
  );
}
