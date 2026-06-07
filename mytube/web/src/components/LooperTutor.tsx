import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, ChevronLeft, ChevronRight, Bookmark, Save } from 'lucide-react';
import { MediaMetadata, incrementLoopCount } from '../lib/storage';

interface LooperTutorProps {
  file: File;
  metadata: MediaMetadata;
}

const LooperTutor: React.FC<LooperTutorProps> = ({ file, metadata }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loopStart, setLoopStart] = useState(0);
  const [loopEnd, setLoopEnd] = useState(0);
  const [isLooping, setIsLooping] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [localLoopCount, setLocalLoopCount] = useState(metadata.loopCount);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileUrl = useRef(URL.createObjectURL(file));

  useEffect(() => {
    return () => URL.revokeObjectURL(fileUrl.current);
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
      if (isLooping && video.currentTime >= loopEnd) {
        video.currentTime = loopStart;
        handleLoopEnd();
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
      setLoopEnd(video.duration);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
  }, [isLooping, loopStart, loopEnd]);

  const handleLoopEnd = async () => {
    setLocalLoopCount(prev => prev + 1);
    await incrementLoopCount(metadata.id);
  };

  const togglePlay = () => {
    if (videoRef.current?.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current?.pause();
      setIsPlaying(false);
    }
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="relative group bg-black rounded-3xl overflow-hidden aspect-video shadow-2xl border border-zinc-200 dark:border-zinc-800">
        <video 
          ref={videoRef} 
          src={fileUrl.current} 
          className="w-full h-full"
          onClick={togglePlay}
          playsInline
        />
        
        {/* Overlay Controls */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6 space-y-4">
          <div className="flex items-center justify-between text-white">
            <div className="flex items-center gap-4">
              <button onClick={togglePlay} className="p-2 hover:bg-white/20 rounded-full transition-colors">
                {isPlaying ? <Pause fill="currentColor" /> : <Play fill="currentColor" />}
              </button>
              <span className="text-sm font-medium tabular-nums">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full border border-white/20">
              <span className="text-xs font-bold uppercase tracking-wider">Loops: {localLoopCount}</span>
            </div>
          </div>
          
          <input 
            type="range" 
            min="0" 
            max={duration} 
            step="0.1" 
            value={currentTime} 
            onChange={(e) => {
              if (videoRef.current) videoRef.current.currentTime = parseFloat(e.target.value);
            }}
            className="w-full accent-blue-600 h-1 bg-white/20 rounded-full cursor-pointer"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* A-B Loop Controls */}
        <div className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <RotateCcw size={20} className="text-blue-600" />
              A-B Repetition
            </h3>
            <button 
              onClick={() => setIsLooping(!isLooping)}
              className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest transition-all ${
                isLooping ? 'bg-blue-600 text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-500'
              }`}
            >
              {isLooping ? 'Looping' : 'Inactive'}
            </button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-500 font-medium">Start Point (A)</span>
              <span className="font-bold tabular-nums text-blue-600">{formatTime(loopStart)}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max={loopEnd} 
              step="0.1" 
              value={loopStart} 
              onChange={(e) => setLoopStart(parseFloat(e.target.value))}
              className="w-full accent-blue-600"
            />
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-500 font-medium">End Point (B)</span>
              <span className="font-bold tabular-nums text-blue-600">{formatTime(loopEnd)}</span>
            </div>
            <input 
              type="range" 
              min={loopStart} 
              max={duration} 
              step="0.1" 
              value={loopEnd} 
              onChange={(e) => setLoopEnd(parseFloat(e.target.value))}
              className="w-full accent-blue-600"
            />
          </div>

          <div className="flex gap-2">
            <button 
              onClick={() => setLoopStart(currentTime)}
              className="flex-1 py-3 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-2xl font-semibold transition-colors flex items-center justify-center gap-2"
            >
              Set A
            </button>
            <button 
              onClick={() => setLoopEnd(currentTime)}
              className="flex-1 py-3 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-2xl font-semibold transition-colors flex items-center justify-center gap-2"
            >
              Set B
            </button>
          </div>
        </div>

        {/* Speed & Bookmarks */}
        <div className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl space-y-6">
          <div className="space-y-4">
            <h3 className="font-bold text-lg">Playback Speed</h3>
            <div className="flex gap-2">
              {[0.5, 0.75, 1, 1.25, 1.5, 2].map((speed) => (
                <button
                  key={speed}
                  onClick={() => {
                    setPlaybackSpeed(speed);
                    if (videoRef.current) videoRef.current.playbackRate = speed;
                  }}
                  className={`flex-1 py-2 rounded-xl text-sm font-bold transition-all ${
                    playbackSpeed === speed 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700'
                  }`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
             <div className="flex items-center justify-between">
                <h3 className="font-bold text-lg flex items-center gap-2">
                  <Bookmark size={20} className="text-blue-600" />
                  Loop Stats
                </h3>
             </div>
             <div className="p-4 bg-zinc-50 dark:bg-zinc-950 rounded-2xl border border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
                <span className="text-zinc-500 font-medium">Total repetitions this session:</span>
                <span className="text-2xl font-bold text-blue-600">{localLoopCount}</span>
             </div>
             <p className="text-xs text-zinc-400 leading-relaxed italic">
               Progress is saved locally on your device for privacy.
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LooperTutor;
