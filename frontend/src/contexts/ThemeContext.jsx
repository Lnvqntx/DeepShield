import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext({
  theme: 'dark',               // 'dark' | 'light'
  setTheme: (theme) => {},     // updater
  toggleTheme: () => {},       // convenience
});

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Load persisted theme or default to dark
    const saved = localStorage.getItem('theme');
    return saved || 'dark';
  });

  useEffect(() => {
    // Apply theme to <body> via data attribute – easiest for global CSS
    document.documentElement.setAttribute('data-theme', theme);
    // Persist selection
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  const value = { theme, setTheme, toggleTheme };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
