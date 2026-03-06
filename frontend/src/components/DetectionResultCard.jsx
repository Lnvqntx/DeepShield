// src/components/DetectionResultCard.jsx
import React from 'react';

// status: 'REAL'|'AI-GENERATED FAKE', confidence: 0..100
export default function DetectionResultCard({ status, confidence }) {
  const isReal = status === 'REAL';
  const color = isReal ? 'var(--success)' : 'var(--danger)';
  return (
    <div className="card" style={{padding:16, borderColor: color}}>
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8}}>
        <div className="card-title">Detection Result</div>
        <div className="badge" style={isReal ? {color:'#bbf7d0', background:'rgba(34,197,94,0.12)', borderColor:'rgba(34,197,94,0.35)'} : {color:'#fecaca', background:'rgba(239,68,68,0.12)', borderColor:'rgba(239,68,68,0.35)'}}>
          <span style={{width:8, height:8, borderRadius:999, background:color}}/>
          {status}
        </div>
      </div>
      <div style={{fontSize:14, color:'var(--text-secondary)'}}>Confidence</div>
      <div style={{fontWeight:800, fontSize:28, color}}>{Math.round(confidence)}%</div>
      <div className="divider"/>
      <div style={{display:'flex', gap:8}}>
        <div className="badge badge-info">Updates ~2s</div>
        <div className="badge" style={{color:'#ddd', background:'rgba(255,255,255,0.05)'}}>Model: AASIST + XLSR-53</div>
      </div>
    </div>
  );
}
