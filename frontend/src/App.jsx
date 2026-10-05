import { useState } from 'react';
import Navbar from "./components/Navbar";
import ChartWidget from "./components/ChartWidget";
import MarketScreener from "./components/MarketScreener";
import AiAssistant from "./components/AiAssistant";

export default function App() {
  // 1. GLOBAL STATE
  const [globalTicker, setGlobalTicker] = useState('BTC-USD');
  const [aiQuery, setAiQuery] = useState(null);

  // 2. THE MASTER FUNCTION
  // When a user clicks "Analyze" on the table, this runs.
  const handleAnalyze = (ticker) => {
    setGlobalTicker(ticker); // 1. Tell the chart to switch coins
    setAiQuery(`Please provide a quantitative technical analysis for ${ticker}.`); // 2. Tell the AI to generate a report
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 font-sans">
      <Navbar />
      
      <main className="flex-1 grid grid-cols-12 gap-4 p-4 min-h-0">
        
        {/* Left Side (Chart & Screener) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-4 min-h-0">
          
          {/* Chart Panel */}
          <div className="flex-3 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <ChartWidget 
              ticker={globalTicker} 
              setTicker={setGlobalTicker} 
            />
          </div>
          
          {/* Market Screener Panel */}
          <div className="flex-2 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4 overflow-hidden">
            <MarketScreener onAnalyze={handleAnalyze} />
          </div>
          
        </div>

        {/* Right Side (AI Assistant) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <AiAssistant 
            externalQuery={aiQuery} 
            onQueryProcessed={() => setAiQuery(null)} 
          />
        </div>

      </main>
    </div>
  );
}