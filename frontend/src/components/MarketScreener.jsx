import { useEffect, useState } from 'react';
import { List, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';

// 1. Accept the 'onAnalyze' function passed down from App.jsx
export default function MarketScreener({ onAnalyze }) {
  const [coins, setCoins] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/top-coins`);
        const json = await response.json();
        if (json.coins) {
          setCoins(json.coins);
        }
      } catch (err) {
        console.error('Error fetching coins:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCoins();
  }, []);

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex items-center gap-2 mb-4 shrink-0">
        <List className="text-blue-500 w-5 h-5" />
        <h2 className="text-lg font-semibold text-white">Top 50 Market Screener</h2>
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-blue-500 ml-2" />}
      </div>

      <div className="flex-1 overflow-auto min-h-0">
        <table className="w-full text-sm text-left">
          
          <thead className="text-xs text-slate-400 uppercase bg-slate-900 sticky top-0 z-10 shadow-sm">
            <tr>
              <th className="px-4 py-3 font-semibold">Asset</th>
              <th className="px-4 py-3 font-semibold">Price</th>
              <th className="px-4 py-3 font-semibold">24h Change</th>
              <th className="px-4 py-3 font-semibold text-right">Action</th>
            </tr>
          </thead>
          
          <tbody>
            {coins.map((coin) => {
              const isPositive = coin.change_24h_pct >= 0;
              // Format standard pairs for Yahoo Finance (e.g., BTC -> BTC-USD)
              const standardTicker = `${coin.symbol}-USD`;
              
              return (
                <tr 
                  key={coin.id} 
                  className="border-b border-slate-800/50 hover:bg-slate-800/50 transition-colors"
                >
                  <td className="px-4 py-3 text-white flex items-center gap-2">
                    <span className="text-slate-500 w-5 text-xs text-right">{coin.rank}</span>
                    <span className="font-medium">{coin.symbol}</span>
                    <span className="text-slate-500 text-xs hidden 2xl:inline truncate max-w-100px">
                      {coin.name}
                    </span>
                  </td>
                  
                  <td className="px-4 py-3 font-mono">
                    ${coin.price_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
                  </td>
                  
                  <td className={`px-4 py-3 font-mono ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    <div className="flex items-center gap-1">
                      {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      {Math.abs(coin.change_24h_pct)}%
                    </div>
                  </td>
                  
                  <td className="px-4 py-3 text-right">
                    <button 
                      className="px-3 py-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded hover:bg-blue-500/20 hover:text-blue-300 transition-colors text-xs font-medium cursor-pointer"
                      // 2. Trigger the App.jsx function when clicked!
                      onClick={() => onAnalyze(standardTicker)}
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
          
        </table>
      </div>
    </div>
  );
}