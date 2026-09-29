// File: src/Dashboard.jsx

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-50 p-8 text-slate-900 font-sans">
      
      {/* Header section with an input and button */}
      <div className="flex items-center justify-between mb-8 max-w-6xl mx-auto">
        <h2 className="text-2xl font-bold">Quantitative Analyst</h2>
        <div className="flex gap-2">
          <input 
            type="text" 
            placeholder="Search ticker (e.g. BTC-USD)" 
            className="border border-slate-300 rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg font-medium">
            Analyze
          </button>
        </div>
      </div>

      {/* The Grid layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        
        {/* Metric Card 1 */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">Current Price</span>
          <span className="text-3xl font-bold mt-1 text-slate-900">$64,200</span>
        </div>

        {/* Metric Card 2 (With Status Badge) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-start">
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">AI Stance</span>
          <span className="inline-flex items-center px-3 py-1 mt-2 rounded-full text-sm font-bold bg-emerald-100 text-emerald-800">
            BULLISH
          </span>
        </div>

        {/* Metric Card 3 */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">14-Day RSI</span>
          <span className="text-3xl font-bold mt-1 text-slate-900">72.5</span>
        </div>

      </div>
    </div>
  );
}