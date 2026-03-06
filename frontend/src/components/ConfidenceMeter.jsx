// src/components/ConfidenceMeter.jsx
import React from 'react';

// value: 0..100, label: string
export default function ConfidenceMeter({ value, label }) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct >= 80 ? 'var(--success)' : pct >= 60 ? 'var(--warning)' : 'var(--danger)';
  return (
    <div className="card" style={{padding:14}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8}}>
        <div style={{fontWeight:800}}>{label}</div>
        <div style={{fontWeight:800, color}}>{pct}%</div>
      </div>
      <div style={{height:10, background:'rgba(255,255,255,0.05)', borderRadius:999, overflow:'hidden', border:'1px solid var(--border)'}}>
        <div style={{width:`${pct}%`, height:'100%', background: `linear-gradient(90deg, ${color}, rgba(255,255,255,0.2))`, transition:'width 200ms'}}/>
      </div>
    </div>
  );
}
