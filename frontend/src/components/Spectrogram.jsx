// src/components/Spectrogram.jsx
import React, { useEffect, useRef } from 'react';

// Draws a simple time-frequency intensity image based on an AnalyserNode
export default function Spectrogram({ analyser, height = 160 }) {
  const ref = useRef(null);
  const raf = useRef(0);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let rafId;

    const bufferLength = analyser ? analyser.frequencyBinCount : 1024;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      rafId = requestAnimationFrame(draw);
      if (!analyser) return;
      analyser.getByteFrequencyData(dataArray);

      const w = canvas.width;
      const h = canvas.height;
      // scroll
      const imageData = ctx.getImageData(1, 0, w - 1, h);
      ctx.putImageData(imageData, 0, 0);

      // rightmost column
      for (let y = 0; y < h; y++) {
        const i = Math.floor((y / h) * bufferLength);
        const v = dataArray[i] / 255;
        const color = `rgba(${Math.floor(255*v)}, ${Math.floor(80*v)}, ${Math.floor(20*v)}, 0.9)`;
        ctx.fillStyle = color;
        ctx.fillRect(w - 1, y, 1, 1);
      }
    };

    draw();
    return () => cancelAnimationFrame(rafId);
  }, [analyser, height]);

  return (
    <canvas ref={ref} width="1000" height={height} className="waveform" style={{height, borderRadius:12}}/>
  );
}
