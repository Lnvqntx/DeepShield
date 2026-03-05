import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

export default function ThemeToggle({ size = 18 }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="btn btn-ghost"
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
      style={{ display: 'flex', alignItems: 'center', gap: 8 }}
    >
      {/* Sun / Moon Icon (inline SVG) */}
      {theme === 'dark' ? (
        // Sun (light theme)
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
          <path d="M12 4V2m0 20v-2M4 12H2m20 0h-2M5.64 5.64L4.22 4.22m15.56 15.56l-1.42-1.42M18.36 5.64l1.42-1.42M5.64 18.36l-1.42 1.42"
                stroke="var(--text-secondary)" strokeWidth="1.5" strokeLinecap="round"/>
          <circle cx="12" cy="12" r="4" stroke="var(--accent)" strokeWidth="1.5"/>
        </svg>
      ) : (
        // Moon (dark theme)
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
          <path d="M21 12.79A9 9 0 1111.21 3c.04-.01.09-.01.13-.01A7 7 0 0021 12.79z"
                stroke="var(--accent)" strokeWidth="1.5"/>
        </svg>
      )}
      <span style={{fontSize:12, color:'var(--text-secondary)'}}>
        {theme === 'dark' ? 'Light' : 'Dark'}
      </span>
    </button>
  );
}
