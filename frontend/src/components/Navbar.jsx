import { useState, useEffect } from 'react';
import { Activity, Clock } from 'lucide-react';

// 1. We create a simple, clean SVG component for the GitHub logo
const GithubIcon = ({ className }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
    <path d="M9 18c-4.51 2-5-2-7-2" />
  </svg>
);

export default function Navbar() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-900 shrink-0">
      
      {/* Left Side: Brand Logo */}
      <div className="flex items-center gap-3">
        <div className="bg-blue-500/10 p-2 rounded-lg border border-blue-500/20">
          <Activity className="text-blue-500 w-5 h-5" />
        </div>
        <h1 className="text-xl font-bold tracking-tight text-white">
          Quant<span className="text-blue-500">AI</span> Analyst
        </h1>
      </div>

      {/* Right Side: Status & Tools */}
      <div className="flex items-center gap-6 text-sm text-slate-400">
        
        {/* 2. Live Local Clock (Added hour12: false for 24-hour format) */}
        <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded border border-slate-800">
          <Clock className="w-4 h-4 text-slate-500" />
          <span className="font-mono text-slate-300">
            {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}
          </span>
        </div>

        {/* Divider */}
        <div className="h-5 w-px bg-slate-700 hidden sm:block"></div>

        {/* 3. GitHub Link using the custom SVG */}
        <a 
          href="https://github.com/GeorgeTamba/quantitative-market-analyst.git" 
          target="_blank" 
          rel="noreferrer"
          className="hover:text-white transition-colors cursor-pointer"
        >
          <GithubIcon className="w-5 h-5" />
        </a>
        
      </div>
    </header>
  );
}