import React, { useEffect, useRef, useState } from 'react';
import Waveform from '../components/Waveform.jsx';
import Spectrogram from '../components/Spectrogram.jsx';
import DetectionResultCard from '../components/DetectionResultCard.jsx';
import ConfidenceMeter from '../components/ConfidenceMeter.jsx';

export default function AudioUpload() {
  const [drag, setDrag] = useState(false);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState({ status:'REAL', confidence: 88, language:'English', time: '1.2s' });
  const [audioUrl, setAudioUrl] = useState('');
  const acRef = useRef(null);
  const analyserRef = useRef(null);
  const [srcNode, setSrcNode] = useState(null);

  const onDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const onFile = (e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const handleFile = (f) => {
    if (!/audio\/(wav|mp3)/.test(f.type) && !/\.(wav|mp3)$/i.test(f.name)) {
      alert('Please upload a WAV or MP3 file.');
      return;
    }
    setFile(f);
    const url = URL.createObjectURL(f);
    setAudioUrl(url);

    // Create a simple audio element to extract stream for visualization
    const audio = new Audio(url);
    audio.crossOrigin = 'anonymous';
    audio.play().catch(()=>{});
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    acRef.current = ac;
    const src = ac.createMediaElementSource(audio);
    const analyser = ac.createAnalyser();
    analyser.fftSize = 2048;
    analyserRef.current = analyser;
    src.connect(analyser);
    analyser.connect(ac.destination);
    setSrcNode(ac.createMediaStreamDestination()); // placeholder
    // Simulate analysis result
    const fakeBias = 0.2;
    const isFake = Math.random() < fakeBias;
    const langs = ['English','Hindi','Telugu'];
    const lang = langs[Math.floor(Math.random()*langs.length)];
    setResult({ status: isFake ? 'AI-GENERATED FAKE':'REAL', confidence: 70 + Math.random()*28, language: lang, time: (0.8 + Math.random()*1.8).toFixed(1)+'s' });
  };

  useEffect(() => {
    return () => {
      try { acRef.current?.close(); } catch {}
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  return (
    <div className="grid" style={{gridTemplateColumns:'380px 1fr', gap:16}}>
      <div className="card">
        <div className="card-header"><div className="card-title">Upload Audio</div></div>
        <div className="card-body">
          <div
            className={`dropzone ${drag ? 'dragover' : ''}`}
            onDragOver={(e)=>{e.preventDefault(); setDrag(true);}}
            onDragLeave={()=>setDrag(false)}
            onDrop={onDrop}
          >
            <div style={{fontWeight:800, marginBottom:6}}>Drag & drop WAV/MP3</div>
            <div style={{fontSize:12, color:'var(--text-secondary)', marginBottom:12}}>Supported: WAV, MP3. Max 50MB.</div>
            <button className="btn btn-primary" onClick={()=>document.getElementById('file').click()}>Browse</button>
            <input id="file" type="file" accept=".wav,.mp3,audio/*" style={{display:'none'}} onChange={onFile}/>
          </div>
          {file && (
            <>
              <div className="divider"/>
              <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
                <div style={{fontWeight:700}}>{file.name}</div>
                <div className="badge" style={{background:'var(--surface-hover)', color:'var(--text-secondary)'}}>{(file.size/1024/1024).toFixed(1)} MB</div>
              </div>
              <div style={{marginTop:10}}>
                <audio controls src={audioUrl} style={{width:'100%'}}/>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Detection Analysis</div>
          <div style={{display:'flex', gap:8}}>
            <div className="badge" style={{background:'var(--surface-hover)', color:'var(--text-secondary)'}}>Language: {result.language}</div>
            <div className="badge" style={{background:'var(--surface-hover)', color:'var(--text-secondary)'}}>Processing: {result.time}</div>
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-2" style={{gap:16}}>
            <div>
              <div style={{marginBottom:8, fontWeight:800}}>Waveform</div>
              <Waveform active={!!file} sourceNode={null}/>
            </div>
            <div>
              <div style={{marginBottom:8, fontWeight:800}}>Spectrogram</div>
              <Spectrogram analyser={analyserRef.current}/>
            </div>
          </div>
          <div className="grid grid-2" style={{marginTop:16, gap:16}}>
            <DetectionResultCard status={result.status} confidence={result.confidence}/>
            <ConfidenceMeter value={result.confidence} label="Confidence"/>
          </div>
        </div>
      </div>
    </div>
  );
}
