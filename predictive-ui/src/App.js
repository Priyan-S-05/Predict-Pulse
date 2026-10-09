import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [form, setForm] = useState({
    type: "H", air_temp: "300", process_temp: "310", rotational_speed: "1500", torque: "40", tool_wear: "50"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [autoSim, setAutoSim] = useState(false);

  const failureRate = history.length > 0 
    ? ((history.filter(item => item.status === "FAIL").length / history.length) * 100).toFixed(1) 
    : 0;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  const handlePredict = async (currentForm = form) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: currentForm.type,
          air_temp: parseFloat(currentForm.air_temp),
          process_temp: parseFloat(currentForm.process_temp),
          rotational_speed: parseFloat(currentForm.rotational_speed),
          torque: parseFloat(currentForm.torque),
          tool_wear: parseFloat(currentForm.tool_wear)
        })
      });

      if (!res.ok) throw new Error(`Status: ${res.status}`);
      const data = await res.json();
      setResult(data);

      const newEntry = {
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        ...currentForm,
        prob: parseFloat((data["Failure Probability"] * 100).toFixed(1)),
        status: data["Failure"] ? "FAIL" : "OK",
        failType: data["Failure Type"] || "Healthy"
      };
      
      setHistory((prev) => [...prev, newEntry].slice(-20));
    } catch (err) {
      setError("Cloud API Offline - Check AWS EC2 Connection");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Time,Type,RPM,Torque,Wear,Status,Diagnostic\n"
      + history.map(e => `${e.time},${e.type},${e.rotational_speed},${e.torque},${e.tool_wear},${e.status},${e.failType}`).join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", "PredictPulse_Engine_Log.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    let interval;
    if (autoSim) {
      interval = setInterval(() => {
        const simData = {
          type: ["L", "M", "H"][Math.floor(Math.random() * 3)],
          air_temp: (298 + Math.random() * 12).toFixed(1),
          process_temp: (308 + Math.random() * 12).toFixed(1),
          rotational_speed: Math.floor(1350 + Math.random() * 500).toString(),
          torque: (35 + Math.random() * 40).toFixed(1),
          tool_wear: Math.floor(Math.random() * 240).toString()
        };
        setForm(simData);
        handlePredict(simData);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [autoSim]);

  return (
    <div className="min-h-screen bg-[#080808] text-slate-300 p-4 md:p-10 font-sans">
      
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-10 border-b border-white/5 pb-8 gap-6">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tighter uppercase flex items-center gap-3">
            <span className="w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-[0_0_15px_#22c55e]"></span>
            Predict <span className="text-green-500 italic font-light">Pulse</span>
          </h1>
          <p className="text-gray-500 text-[10px] tracking-[0.4em] font-bold mt-1 uppercase">NASA Turbofan Health Monitor</p>
        </div>
        <button onClick={downloadReport} className="bg-white/5 border border-white/10 px-6 py-3 rounded-2xl text-[10px] font-bold text-white hover:bg-white/10 transition-all uppercase">
          Download Flight Log
        </button>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-[#121212] p-5 rounded-3xl border border-white/5">
          <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Fleet Failure Rate</p>
          <p className="text-2xl font-black text-red-500">{failureRate}%</p>
        </div>
        <div className="bg-[#121212] p-5 rounded-3xl border border-white/5">
          <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">System Runtime</p>
          <p className="text-xl font-bold text-white tracking-tighter uppercase">AWS Cloud Live</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-[#121212] p-8 rounded-[35px] border border-white/5 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xs font-bold uppercase text-gray-400">Engine Telemetry</h3>
              <div onClick={() => setAutoSim(!autoSim)} className={`cursor-pointer w-10 h-5 rounded-full p-1 transition-colors ${autoSim ? 'bg-green-500' : 'bg-gray-700'}`}>
                <motion.div animate={{ x: autoSim ? 20 : 0 }} className="w-3 h-3 bg-white rounded-full" />
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[9px] text-gray-500 uppercase font-bold ml-1">Inlet Temp [K]</label>
                  <input name="air_temp" value={form.air_temp} onChange={handleChange} className="w-full p-3 bg-black rounded-xl border border-white/10 text-sm text-white" />
                </div>
                <div className="space-y-1">
                  <label className="text-[9px] text-gray-500 uppercase font-bold ml-1">Exhaust Temp [K]</label>
                  <input name="process_temp" value={form.process_temp} onChange={handleChange} className="w-full p-3 bg-black rounded-xl border border-white/10 text-sm text-white" />
                </div>
              </div>
              <div className="space-y-1">
                  <label className="text-[9px] text-gray-500 uppercase font-bold ml-1">Fan Speed [RPM]</label>
                  <input name="rotational_speed" value={form.rotational_speed} onChange={handleChange} className="w-full p-3 bg-black rounded-xl border border-white/10 text-sm text-white" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[9px] text-gray-500 uppercase font-bold ml-1">Torque [Nm]</label>
                  <input name="torque" value={form.torque} onChange={handleChange} className="w-full p-3 bg-black rounded-xl border border-white/10 text-sm text-white" />
                </div>
                <div className="space-y-1">
                  <label className="text-[9px] text-gray-500 uppercase font-bold ml-1">Cycle Wear [min]</label>
                  <input name="tool_wear" value={form.tool_wear} onChange={handleChange} className="w-full p-3 bg-black rounded-xl border border-white/10 text-sm text-white" />
                </div>
              </div>
              <button onClick={() => handlePredict()} disabled={loading || autoSim} className={`w-full p-4 rounded-xl font-black text-[11px] uppercase tracking-widest transition-all ${autoSim ? 'bg-gray-800 text-gray-600' : 'bg-green-600 text-white'}`}>
                {loading ? "PROCESSING..." : "MANUAL DIAGNOSTIC"}
              </button>
            </div>
          </div>

          <AnimatePresence>
            {result?.Failure && (
              <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-red-500/10 border border-red-500/50 p-6 rounded-[35px]">
                <p className="text-[10px] text-red-500 font-bold uppercase mb-2">Critical Diagnostic Alert</p>
                <h4 className="text-2xl font-black text-red-500 uppercase italic leading-none">{result["Failure Type"]}</h4>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="lg:col-span-8 space-y-8">
          <div className="bg-[#121212] p-10 rounded-[50px] border border-white/5 relative">
            <div className="flex flex-col md:flex-row justify-between items-center gap-8">
              <div>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Engine Pulse State</p>
                <h2 className={`text-6xl font-black tracking-tighter ${result?.Failure ? 'text-red-500' : 'text-green-500'}`}>
                  {result ? (result.Failure ? "FAILURE" : "NORMAL") : "STANDBY"}
                </h2>
              </div>
              <div className="text-center px-10 py-6 bg-black/40 rounded-3xl border border-white/10 min-w-[220px]">
                <p className="text-[10px] text-gray-500 font-bold uppercase mb-1">Failure Probability</p>
                <p className={`text-6xl font-mono font-black ${result?.Failure ? 'text-red-500' : 'text-yellow-500'}`}>
                  {result ? (result["Failure Probability"] * 100).toFixed(1) : "00.0"}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#121212] p-8 rounded-[40px] border border-white/5">
             <h3 className="text-xs font-bold text-gray-500 uppercase mb-8 tracking-widest">Real-Time Probability Stream</h3>
             <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                    <XAxis dataKey="time" stroke="#444" fontSize={10} tickMargin={10} />
                    <YAxis domain={[0, 100]} stroke="#444" fontSize={10} />
                    <Tooltip contentStyle={{backgroundColor: '#000', border: 'none', borderRadius: '15px'}} />
                    <Line type="monotone" dataKey="prob" stroke="#22c55e" strokeWidth={4} dot={{r: 4, fill: '#22c55e'}} />
                  </LineChart>
                </ResponsiveContainer>
             </div>
          </div>
        </div>
      </div>
      {error && <p className="mt-6 text-center text-red-500 font-mono text-xs uppercase tracking-widest">{error}</p>}
    </div>
  );
}

export default App;