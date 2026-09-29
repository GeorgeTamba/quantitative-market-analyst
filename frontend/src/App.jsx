import Navbar from "./components/Navbar";
import ChartWidget from "./components/ChartWidget";
import MarketScreener from "./components/MarketScreener";
import AiAssistant from "./components/AiAssistant";

export default function App() {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 font-sans">
      <Navbar />
      
      {/* Main Layout Grid */}
      <main className="flex-1 grid grid-cols-12 gap-4 p-4 min-h-0">
        
        {/* Left Side (Chart & Screener) - takes up 8 of 12 columns */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-4 min-h-0">
          
          {/* Chart Panel (Takes up 60% of vertical height) */}
          <div className="flex-3 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <ChartWidget />
          </div>
          
          {/* Market Screener Panel (Takes up 40% of vertical height) */}
          <div className="flex-2 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4 overflow-hidden">
            <MarketScreener />
          </div>
          
        </div>

        {/* Right Side (AI Assistant) - takes up 4 of 12 columns */}
        <div className="col-span-12 lg:col-span-4 flex flex-col min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <AiAssistant />
        </div>

      </main>
    </div>
  );
}