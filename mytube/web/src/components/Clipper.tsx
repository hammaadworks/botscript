import React, { useState, useRef, useEffect } from 'react';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';
import { Scissors, Download, Loader2, Play } from 'lucide-react';

interface ClipperProps {
  file: File;
}

const Clipper: React.FC<ClipperProps> = ({ file }) => {
  const [ffmpeg] = useState(() => new FFmpeg());
  const [loaded, setLoaded] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    loadFFmpeg();
  }, []);

  const loadFFmpeg = async () => {
    const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm';
    await ffmpeg.load({
      coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
      wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
    });
    setLoaded(true);
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const handleLoadedMetadata = () => {
      setDuration(video.duration);
      setEndTime(video.duration);
    };
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    return () => video.removeEventListener('loadedmetadata', handleLoadedMetadata);
  }, [file]);

  const transcode = async () => {
    setProcessing(true);
    const inputName = 'input' + file.name.substring(file.name.lastIndexOf('.'));
    const outputName = 'output' + file.name.substring(file.name.lastIndexOf('.'));
    
    await ffmpeg.writeFile(inputName, await fetchFile(file));
    
    // -ss (start time), -to (end time), -c copy (fast trim without re-encoding)
    await ffmpeg.exec([
        '-ss', startTime.toString(),
        '-to', endTime.toString(),
        '-i', inputName,
        '-c', 'copy',
        outputName
    ]);
    
    const data = await ffmpeg.readFile(outputName);
    const url = URL.createObjectURL(new Blob([(data as any).buffer], { type: file.type }));
    setPreviewUrl(url);
    setProcessing(false);
  };

  const downloadClip = () => {
    if (!previewUrl) return;
    const a = document.createElement('a');
    a.href = previewUrl;
    a.download = `clip_${file.name}`;
    a.click();
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Precision Clipper</h2>
        <p className="text-zinc-500">Trim your media locally using WebAssembly.</p>
      </div>

      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8 space-y-8 shadow-sm">
        <div className="aspect-video bg-black rounded-2xl overflow-hidden shadow-inner border border-zinc-200 dark:border-zinc-800">
           <video ref={videoRef} src={URL.createObjectURL(file)} className="w-full h-full" controls />
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-zinc-500">Start Time</label>
              <div className="flex items-center gap-3">
                <input 
                  type="number" 
                  value={startTime} 
                  onChange={(e) => setStartTime(parseFloat(e.target.value))}
                  className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2 font-mono"
                />
                <span className="text-xs text-zinc-400 font-medium tabular-nums w-12">{formatTime(startTime)}</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-zinc-500">End Time</label>
              <div className="flex items-center gap-3">
                <input 
                  type="number" 
                  value={endTime} 
                  onChange={(e) => setEndTime(parseFloat(e.target.value))}
                  className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2 font-mono"
                />
                <span className="text-xs text-zinc-400 font-medium tabular-nums w-12">{formatTime(endTime)}</span>
              </div>
            </div>
          </div>

          <div className="relative h-2 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
             <div 
               className="absolute h-full bg-blue-600/20" 
               style={{ 
                 left: `${(startTime / duration) * 100}%`, 
                 width: `${((endTime - startTime) / duration) * 100}%` 
               }} 
             />
          </div>

          {!previewUrl ? (
            <button
              onClick={transcode}
              disabled={!loaded || processing}
              className="w-full py-4 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-black rounded-2xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-all disabled:opacity-50"
            >
              {processing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Processing on your device...
                </>
              ) : (
                <>
                  <Scissors size={20} />
                  Generate Clip
                </>
              )}
            </button>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30 rounded-2xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white">
                    <Download size={20} />
                  </div>
                  <div>
                    <p className="font-bold text-green-700 dark:text-green-400">Clip Ready</p>
                    <p className="text-xs text-green-600/70">Processed locally with FFmpeg WASM</p>
                  </div>
                </div>
                <button 
                  onClick={downloadClip}
                  className="px-6 py-2 bg-green-600 text-white rounded-xl font-bold hover:bg-green-700 transition-colors"
                >
                  Download
                </button>
              </div>
              <button 
                onClick={() => setPreviewUrl(null)}
                className="w-full py-3 text-zinc-500 text-sm font-medium hover:text-zinc-900 transition-colors"
              >
                Create another clip
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Clipper;
