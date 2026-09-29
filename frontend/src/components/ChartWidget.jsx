import { useEffect, useRef, useState } from 'react';
// Notice we now import CandlestickSeries specifically
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import { LineChart, Loader2 } from 'lucide-react';

export default function ChartWidget() {
  const chartContainerRef = useRef();
  const [ticker, setTicker] = useState('BTC-USD'); 
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // A. Initialize the TradingView Chart Canvas
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8', 
      },
      grid: {
        vertLines: { color: '#1e293b' }, 
        horzLines: { color: '#1e293b' },
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
    });

    // B. Create the Candlestick Series (NEW VERSION 5 SYNTAX)
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',      
      downColor: '#ef4444',    
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    // C. Fetch Data from your Python Backend
    const fetchChartData = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/chart/${ticker}`);
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

    // D. Make it Responsive
    const handleResize = () => {
      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
      });
    };
    window.addEventListener('resize', handleResize);

    // E. Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [ticker]); 

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <LineChart className="text-blue-500 w-5 h-5" />
          <h2 className="text-lg font-semibold text-white">Market Chart</h2>
        </div>
        
        <div className="flex items-center gap-2">
          <input 
            type="text" 
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g. BTC-USD"
            className="bg-slate-950 border border-slate-700 rounded-md px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500 w-32"
          />
          {isLoading && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
        </div>
      </div>

      <div className="flex-1 w-full min-h-0 relative">
        <div ref={chartContainerRef} className="absolute inset-0" />
      </div>
    </div>
  );
}