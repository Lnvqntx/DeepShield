import React from 'react';

export default function SystemArchitecture() {
  const stages = [
    { title:'Microphone / Audio File', desc:'Live stream or file upload (WAV/MP3).', icon:<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 1v6m0 6v6m9-9a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title:'wav2vec2‑xlsr‑53', desc:'Self‑supervised multilingual feature extraction.', icon:<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 7h18M6 3h12M7 21h10" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title:'AASIST Anti‑Spoofing', desc:'Graph‑based anti‑spoofing classifier for deepfake detection.', icon:<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 3l8 4v6c0 5-8 8-8 8s-8-3-8-8V7l8-4z" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title:'Prediction: REAL / FAKE', desc:'Confidence scores and chunk‑level outputs.', icon:<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="1.5"/></svg> },
  ];

  return (
    <div className="card">
      <div className="card-header"><div className="card-title">System Architecture</div></div>
      <div className="card-body">
        <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:16}}>
          {stages.map((s,i) => (
            <div key={i} className="glass" style={{padding:14, borderRadius:12}}>
              <div style={{display:'flex', alignItems:'center', gap:10, marginBottom:6}}>
                <div className="icon">{s.icon}</div>
                <div style={{fontWeight:800}}>{s.title}</div>
              </div>
              <div style={{color:'var(--text-secondary)'}}>{s.desc}</div>
              {i < stages.length - 1 && (
                <div style={{marginTop:10, display:'flex', justifyContent:'flex-end', color:'var(--accent)'}}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="divider"/>
        <div style={{display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12}}>
          <div className="glass" style={{padding:12}}>
            <div style={{fontWeight:800}}>Data In</div>
            <div className="card-subtitle">Streaming buffers, chunking 2s</div>
          </div>
          <div className="glass" style={{padding:12}}>
            <div style={{fontWeight:800}}>Feature Pipeline</div>
            <div className="card-subtitle">128‑d embeddings, per‑chunk</div>
          </div>
          <div className="glass" style={{padding:12}}>
            <div style={{fontWeight:800}}>Inference</div>
            <div className="card-subtitle">On‑device / edge with fallback</div>
          </div>
        </div>
      </div>
    </div>
  );
}
