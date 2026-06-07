import React, { useState, useRef, useEffect } from 'react';
import { Upload, Repeat, Scissors, Play, Info, CheckCircle2, History } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import LooperTutor from './components/LooperTutor';
import Clipper from './components/Clipper';
import { getAllMedia, MediaMetadata, saveMediaMetadata } from './lib/storage';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'looper' | 'clipper' | 'history'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mediaMetadata, setMediaMetadata] = useState<MediaMetadata | null>(null);
  const [history, setHistory] = useState<MediaMetadata[]>([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    const items = await getAllMedia();
    setHistory(items.sort((a, b) => b.lastModified - a.lastModified));
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = async (file: File) => {
    setSelectedFile(file);
    const id = `${file.name}-${file.size}-${file.lastModified}`;
    const metadata: MediaMetadata = {
      id,
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified,
      loopCount: 0,
      savedLoops: []
    };
    setMediaMetadata(metadata);
    await saveMediaMetadata(metadata);
    loadHistory();
    setActiveTab('looper');
  };

  const navItems = [
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'looper', label: 'Looper', icon: Repeat },
    { id: 'clipper', label: 'Clipper', icon: Scissors },
    { id: 'history', label: 'History', icon: History },
  ];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-100 font-sans selection:bg-blue-100 dark:selection:bg-blue-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">W</span>
            </div>
            <span className="font-semibold text-xl tracking-tight">Wgetube</span>
          </div>
          <div className="flex gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                  activeTab === item.id 
                    ? 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-black' 
                    : 'hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
                }`}
              >
                <item.icon size={16} />
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 pt-32 pb-20">
        <AnimatePresence mode="wait">
          {activeTab === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center justify-center text-center space-y-8"
            >
              <div className="space-y-4 max-w-lg">
                <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                  Memorize through <span className="text-blue-600 italic">repetition</span>.
                </h1>
                <p className="text-lg text-zinc-500 dark:text-zinc-400">
                  Upload your downloaded media to start looping, tracking progress, and clipping scenes.
                </p>
              </div>

              <label className="group relative w-full max-w-xl h-64 border-2 border-dashed border-zinc-300 dark:border-zinc-800 rounded-3xl flex flex-col items-center justify-center gap-4 cursor-pointer hover:border-blue-500 dark:hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all duration-300">
                <input type="file" className="hidden" onChange={handleFileChange} accept="video/*,audio/*" />
                <div className="w-16 h-16 bg-white dark:bg-zinc-900 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Upload className="text-blue-600" />
                </div>
                <div className="text-center">
                  <p className="font-semibold text-lg">Drop your file here</p>
                  <p className="text-sm text-zinc-500">Video or Audio files</p>
                </div>
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl mt-12">
                {[
                  { title: 'Any Source', desc: 'Use our CLI to download from anywhere.', icon: Info },
                  { title: 'Precision Loops', desc: 'Set A-B points for perfect repetition.', icon: Repeat },
                  { title: 'Local Clipping', desc: 'Trim and save clips in your browser.', icon: Scissors },
                ].map((feature, i) => (
                  <div key={i} className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl text-left space-y-2">
                    <feature.icon className="text-blue-600 mb-2" size={20} />
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-zinc-500 leading-relaxed">{feature.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'looper' && selectedFile && (
            <motion.div key="looper" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <LooperTutor file={selectedFile} metadata={mediaMetadata!} />
            </motion.div>
          )}

          {activeTab === 'looper' && !selectedFile && (
            <motion.div key="looper-empty" className="text-center py-20 text-zinc-500">
              Please upload a file first.
            </motion.div>
          )}

          {activeTab === 'clipper' && selectedFile && (
            <motion.div key="clipper" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Clipper file={selectedFile} />
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              <h2 className="text-2xl font-bold">Recent Media</h2>
              <div className="grid grid-cols-1 gap-4">
                {history.map((item) => (
                  <div 
                    key={item.id} 
                    className="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl flex items-center justify-between hover:border-blue-500 transition-colors cursor-pointer group"
                    onClick={() => {
                      // Note: We can't actually restore the File object from IDB easily without File System Access API
                      // For now, this is just a log. In a full app, we'd use handles.
                      alert("Please re-upload the file to continue. (File handle support coming soon)");
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-zinc-100 dark:bg-zinc-800 rounded-xl flex items-center justify-center">
                        <Play size={20} className="text-zinc-400 group-hover:text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">{item.name}</h4>
                        <p className="text-xs text-zinc-500">{new Date(item.lastModified).toLocaleDateString()} • {item.loopCount} loops</p>
                      </div>
                    </div>
                    <CheckCircle2 className="text-green-500" size={20} />
                  </div>
                ))}
                {history.length === 0 && <p className="text-center py-10 text-zinc-500">No history found.</p>}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="fixed bottom-0 w-full px-6 py-4 flex justify-center pointer-events-none">
        <div className="bg-zinc-900 dark:bg-white text-white dark:text-black px-4 py-2 rounded-full text-xs font-medium shadow-2xl pointer-events-auto">
          Built for Pro Memorization
        </div>
      </footer>
    </div>
  );
};

export default App;
