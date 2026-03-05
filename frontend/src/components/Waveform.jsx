// src/components/Waveform.jsx
import React, { useEffect, useRef, useState } from 'react';

// Props: { active: boolean, sourceNode: MediaStreamAudioSourceNode | null, height?: number }
export default function Waveform({ active, sourceNode, height = 160 }) {
  const canvasRef = useRef(null);
  const rafRef = useRef(0);
  const [paused, setPaused] = useState(!active);

  useEffect(() => {
    setPaused(!active);
  }, [active]);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let analyser, dataArray, bufferLength;

    const setup = async () => {
      try {
        const ac = new (window.AudioContext || window.webkitAudioContext)();
        let node;
        if (sourceNode) {
          node = sourceNode;
        } else {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          node = ac.createMediaStreamSource(stream);
        }
        analyser = ac.createAnalyser();
        analyser.fftSize = 1024;
        bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        node.connect(analyser);

        const draw = () => {
          rafRef.current = requestAnimationFrame(draw);
          if (paused) return;
          analyser.getByteTimeDomainData(dataArray);

          // Background
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
          grad.addColorStop(0, 'rgba(249,115,22,0.08)');
          grad.addColorStop(1, 'rgba(249,115,22,0.02)');
          ctx.fillStyle = grad;
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          // Wave
          ctx.lineWidth = 2;
          ctx.strokeStyle = 'rgba(249,115,22,0.8)';
          ctx.beginPath();
          const sliceWidth = canvas.width / bufferLength;
          let x = 0;
          for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = (v * canvas.height) / 2;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
            x += sliceWidth;
          }
          ctx.lineTo(canvas.width, canvas.height / 2);
          ctx.stroke();

          // Glow
          ctx.shadowColor = 'rgba(249,115,22,0.35)';
          ctx.shadowBlur = 8;
          ctx.stroke();
          ctx.shadowBlur = 0;
        };
        draw();
      } catch (e) {
        console.warn('Waveform setup failed', e);
      }
    };

    setup();

    return () => {
      cancelAnimationFrame(rafRef.current);
    };
  }, [sourceNode, paused]);

  return (
    <canvas ref={canvasRef} className="waveform" style={{height}} width="1000" height={height} />
  );
}
