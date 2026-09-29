import { useState, useEffect } from 'react';
import { Activity, Clock, Code } from 'lucide-react';

export default function Navbar() {
  const [time, setTime] = useState(new Date());

  // Update the clock every minute
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
        
        {/* Live Local Clock */}
        <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded border border-slate-800">
          <Clock className="w-4 h-4 text-slate-500" />
          <span className="font-mono text-slate-300">
            {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* API Status Indicator */}
        <div className="hidden sm:flex items-center gap-2">
          <div className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
          </div>
          <span className="font-medium text-slate-300">API Connected</span>
        </div>

        {/* Divider */}
        <div className="h-5 w-px bg-slate-700 hidden sm:block"></div>

        {/* GitHub Link (You can update this href later) */}
        <a 
          href="https://github.com" 
          target="_blank" 
          rel="noreferrer"
          className="hover:text-white transition-colors cursor-pointer"
        >
          <Code className="w-5 h-5" />
        </a>
        
      </div>
    </header>
  );
}