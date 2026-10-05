import { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Loader2 } from 'lucide-react';

// 1. We added props to accept commands from the outside (App.jsx)
export default function AiAssistant({ externalQuery, onQueryProcessed }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your quantitative AI assistant. Ask me to analyze any coin, compare metrics, or explain market trends.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 2. We modified this function to accept custom text, not just form events
  const handleSendMessage = async (e, customText = null) => {
    if (e) e.preventDefault();
    
    const userMessage = customText || input.trim();
    if (!userMessage) return;
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    if (!customText) setInput(''); // Only clear input if user typed it
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage }) 
      });
      
      const data = await response.json();
      const aiText = data.response || data.result || data.message || JSON.stringify(data);
      
      setMessages(prev => [...prev, { role: 'assistant', content: aiText }]);
    } catch (error) {
      console.error("Error communicating with AI:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, my backend server isn't responding. Check the FastAPI terminal!" }]);
    } finally {
      setIsLoading(false);
    }
  };

  // 3. This listens for clicks from the Market Screener table
  useEffect(() => {
    if (externalQuery) {
      // setTimeout pushes the state updates to the next tick, safely bypassing the cascading render warning
      setTimeout(() => {
        handleSendMessage(null, externalQuery);
        onQueryProcessed(); 
      }, 0);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalQuery]);

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex items-center gap-2 pb-4 mb-4 border-b border-slate-800 shrink-0">
        <Bot className="text-blue-500 w-6 h-6" />
        <h2 className="text-lg font-semibold text-white">Quant AI</h2>
      </div>

      <div className="flex-1 overflow-y-auto min-h-0 pr-2 flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-700'}`}>
              {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-blue-400" />}
            </div>
            
            <div className={`p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-200 rounded-tl-none whitespace-pre-wrap'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-blue-400" />
            </div>
            <div className="p-3 rounded-lg bg-slate-800 text-slate-200 rounded-tl-none flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span className="text-sm text-slate-400">Analyzing market data...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="mt-4 pt-4 border-t border-slate-800 shrink-0 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Gemini to analyze a coin..."
          className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}