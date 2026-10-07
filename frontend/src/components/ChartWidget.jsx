import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import { LineChart, Loader2 } from 'lucide-react';

export default function ChartWidget({ ticker, setTicker }) {
  const chartContainerRef = useRef();
  const [isLoading, setIsLoading] = useState(false);
  
  // 1. Change the default timeframe to 1 Day candles
  const [timeframe, setTimeframe] = useState('1D'); 

  useEffect(() => {
    const isIntraday = timeframe === '15M' || timeframe === '1H';
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8', 
      },
      grid: {
        vertLines: { color: '#1e293b' }, 
        horzLines: { color: '#1e293b' },
      },
      timeScale: {
        timeVisible: isIntraday,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
    });

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',      
      downColor: '#ef4444',    
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    const fetchChartData = async () => {
      setIsLoading(true);
      try {
        // 2. NEW: Append the active timeframe to the Python API URL
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chart/${ticker}?timeframe=${timeframe}`);
        const json = await response.json();
        
        if (json.data) {
          candlestickSeries.setData(json.data);
          chart.timeScale().fitContent(); 
        }
      } catch (err) {
        console.error('Error fetching chart data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChartData();

    const handleResize = () => {
      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
      });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  // 3. NEW: Add 'timeframe' to this array so React redraws the chart when a button is clicked
  }, [ticker, timeframe]); 

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex items-center justify-between mb-4">
        
        {/* Left Side: Title & Loader */}
        <div className="flex items-center gap-2">
          <LineChart className="text-blue-500 w-5 h-5" />
          <h2 className="text-lg font-semibold text-white">Market Chart</h2>
          {isLoading && <Loader2 className="w-4 h-4 animate-spin text-blue-500 ml-2" />}
        </div>
        
        {/* Right Side: Controls */}
        <div className="flex items-center gap-3">
          
          {/* NEW: Timeframe Toggle Buttons */}
          <div className="flex bg-slate-950 rounded-md p-1 border border-slate-800">
            {['15M', '1H', '1D', '1W'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                  timeframe === tf 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <input 
            type="text" 
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g. BTC-USD"
            className="bg-slate-950 border border-slate-700 rounded-md px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500 w-32"
          />
        </div>
      </div>

      <div className="flex-1 w-full min-h-0 relative">
        <div ref={chartContainerRef} className="absolute inset-0" />
      </div>
    </div>
  );
}