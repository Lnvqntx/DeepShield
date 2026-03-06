import React, { useEffect, useRef, useState } from 'react';
import Waveform from '../components/Waveform.jsx';
import Timeline from '../components/Timeline.jsx';
import DetectionResultCard from '../components/DetectionResultCard.jsx';
import ConfidenceMeter from '../components/ConfidenceMeter.jsx';

export default function LiveDetection() {
  const [listening, setListening] = useState(false);
  const [lang, setLang] = useState('English');
  const [result, setResult] = useState({ status: 'REAL', confidence: 92 });
  const [timeline, setTimeline] = useState([
    { id: 1, label: 'Chunk 1', status: 'REAL' },
    { id: 2, label: 'Chunk 2', status: 'REAL' },
    { id: 3, label: 'Chunk 3', status: 'REAL' },
  ]);
  const acRef = useRef(null);
  const sourceRef = useRef(null);

  useEffect(() => {
    let interval;
    if (listening) {
      // simulate prediction every 2s
      interval = setInterval(() => {
        setResult(prev => {
          const fakeBias = 0.18; // 18% chance of fake
          const isFake = Math.random() < fakeBias;
          const conf = isFake ? 65 + Math.random()*30 : 75 + Math.random()*25;
          return { status: isFake ? 'AI-GENERATED FAKE' : 'REAL', confidence: conf };
        });
        setTimeline(prev => {
          const next = prev.slice(-9);
          const idx = next.length + 1;
          const isFake = result.status === 'AI-GENERATED FAKE';
          next.push({ id: Date.now(), label: `Chunk ${idx}`, status: isFake ? 'FAKE' : 'REAL' });
          return next;
        });
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [listening, result.status]);

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const ac = new (window.AudioContext || window.webkitAudioContext)();
      acRef.current = ac;
      const src = ac.createMediaStreamSource(stream);
      sourceRef.current = src;
      setListening(true);
      setResult({ status: 'REAL', confidence: 92 });
      setTimeline([{ id: 1, label:'Chunk 1', status:'REAL' }]);
    } catch (e) {
      alert('Microphone access denied or unavailable.');
      console.error(e);
    }
  };

  const stopListening = () => {
    setListening(false);
    try {
      acRef.current?.close();
    } catch {}
    acRef.current = null;
    sourceRef.current = null;
  };

  return (
    <div className="grid" style={{gridTemplateColumns:'300px 1fr 360px', gap:16}}>
      <div className="card">
        <div className="card-header"><div className="card-title">Microphone Controls</div></div>
        <div className="card-body" style={{display:'flex', flexDirection:'column', gap:12}}>
          <div style={{display:'flex', gap:8}}>
            <button className={`btn ${listening ? 'btn-danger' : 'btn-success'}`} onClick={listening ? stopListening : startListening}>
              {listening ? 'Stop Listening' : 'Start Listening'}
            </button>
            <button className="btn">Mute</button>
          </div>
          <div>
            <div style={{fontSize:12, color:'var(--text-secondary)', marginBottom:6}}>Language</div>
            <select className="input" value={lang} onChange={e=>setLang(e.target.value)}>
              <option>English</option>
              <option>Hindi</option>
              <option>Telugu</option>
            </select>
          </div>
          <div className="divider"/>
          <div className="badge badge-info">Live Model: XLSR-53 + AASIST</div>
          <div style={{fontSize:12, color:'var(--text-muted)'}}>Streaming analysis with 2s update cadence.</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Real‑time Waveform</div>
          <div style={{display:'flex', gap:8}}>
            <div className="badge" style={{background:'var(--surface-hover)', color:'var(--text-secondary)'}}>EN • {lang}</div>
            <div className="badge" style={{background:'var(--surface-hover)', color:'var(--text-secondary)'}}>Latency ~120ms</div>
          </div>
        </div>
        <div className="card-body">
          <Waveform active={listening} sourceNode={sourceRef.current}/>
          <div style={{marginTop:16}}>
            <DetectionResultCard status={result.status} confidence={result.confidence}/>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Chunk Timeline</div></div>
        <div className="card-body" style={{display:'flex', flexDirection:'column', gap:12}}>
          <Timeline items={timeline}/>
          <ConfidenceMeter value={result.confidence} label="Confidence"/>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:8}}>
            <div className="glass" style={{padding:10}}>
              <div style={{fontWeight:800}}>Energy</div>
              <div style={{fontSize:12, color:'var(--text-secondary)'}}>RMS: 0.43</div>
            </div>
            <div className="glass" style={{padding:10}}>
              <div style={{fontWeight:800}}>Pitch</div>
              <div style={{fontSize:12, color:'var(--text-secondary)'}}>F0: 182 Hz</div>
            </div>
          </div>
          <div className="divider"/>
          <div style={{fontSize:12, color:'var(--text-secondary)'}}>Artifacts overlay: enabled</div>
          <div className="badge badge-info">Model health: OK</div>
        </div>
      </div>
    </div>
  );
}
