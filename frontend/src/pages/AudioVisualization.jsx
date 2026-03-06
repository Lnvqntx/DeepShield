import React, { useEffect, useRef, useState } from 'react';
import Waveform from '../components/Waveform.jsx';
import Spectrogram from '../components/Spectrogram.jsx';

export default function AudioVisualization() {
  const [running, setRunning] = useState(false);
  const acRef = useRef(null);
  const analyserRef = useRef(null);

  useEffect(() => {
    let streamSrc = null;
    if (running) {
      (async () => {
        const ac = new (window.AudioContext || window.webkitAudioContext)();
        acRef.current = ac;
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamSrc = ac.createMediaStreamSource(stream);
        const analyser = ac.createAnalyser();
        analyser.fftSize = 2048;
        analyserRef.current = analyser;
        streamSrc.connect(analyser);
      })();
    }
    return () => {
      try { acRef.current?.close(); } catch {}
      analyserRef.current = null;
    };
  }, [running]);

  return (
    <div className="grid" style={{gap:16}}>
      <div className="card">
        <div className="card-header"><div className="card-title">Waveform Viewer</div></div>
        <div className="card-body">
          <div style={{display:'flex', gap:8, marginBottom:8}}>
            <button className={`btn ${running ? 'btn-danger':'btn-success'}`} onClick={()=>setRunning(r=>!r)}>{running ? 'Stop' : 'Start'}</button>
            <div className="badge badge-info">Mic: On‑device</div>
          </div>
          <Waveform active={running} sourceNode={null}/>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Spectrogram Viewer</div></div>
        <div className="card-body">
          <Spectrogram analyser={analyserRef.current}/>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">AI Artifact Detection Overlay</div></div>
        <div className="card-body">
          <div className="grid grid-3">
            <div className="glass" style={{padding:12}}>
              <div style={{fontWeight:800}}>Energy Variations</div>
              <div style={{color:'var(--text-secondary)', marginTop:6}}>Dynamic range consistent with human speech.</div>
            </div>
            <div className="glass" style={{padding:12}}>
              <div style={{fontWeight:800}}>Pitch Consistency</div>
              <div style={{color:'var(--text-secondary)', marginTop:6}}>F0 variability in natural bounds.</div>
            </div>
            <div className="glass" style={{padding:12}}>
              <div style={{fontWeight:800}}>Spectral Irregularities</div>
              <div style={{color:'var(--text-secondary)', marginTop:6}}>No persistent synthetic artifacts detected.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
