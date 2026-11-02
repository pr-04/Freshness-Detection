import React, { useEffect, useRef, useState } from 'react';
import { Camera, RotateCcw, Check, VideoOff } from 'lucide-react';

export default function CameraPreview({ onUsePhoto }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [error, setError] = useState('');
  const [photo, setPhoto] = useState('');
  const [cameraStarted, setCameraStarted] = useState(false);

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
  };

  useEffect(() => () => stopCamera(), []);

  const startCamera = async () => {
    setError('');
    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Camera access requires a supported browser and a secure page (HTTPS or localhost).');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      streamRef.current = stream;
      setCameraStarted(true);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch (cameraError) {
      const messages = {
        NotAllowedError: 'Camera permission was denied. Allow camera access in your browser settings and try again.',
        NotFoundError: 'No camera was found on this device.',
        NotReadableError: 'The camera is busy or unavailable. Close other apps using it and try again.',
      };
      setError(messages[cameraError.name] || 'The camera could not be started. Check your device and browser permissions.');
      stopCamera();
      setCameraStarted(false);
    }
  };

  const capture = () => {
    const video = videoRef.current;
    if (!video?.videoWidth) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    setPhoto(canvas.toDataURL('image/jpeg', 0.92));
  };

  const usePhoto = async () => {
    const response = await fetch(photo);
    const blob = await response.blob();
    onUsePhoto(new File([blob], `freshguard-camera-${Date.now()}.jpg`, { type: 'image/jpeg' }));
    stopCamera();
    setCameraStarted(false);
  };

  return (
    <div className="rounded-2xl border border-stone-800 bg-neutral-900 p-4 sm:p-6 min-h-[360px] text-white space-y-4">
      <div className="flex items-center gap-2 text-emerald-300 text-xs font-semibold"><Camera className="w-4 h-4" /> CAMERA</div>
      {photo ? <img src={photo} alt="Captured produce" className="w-full max-h-[360px] rounded-xl object-contain bg-black" /> : (
        <video ref={videoRef} className="w-full max-h-[360px] rounded-xl bg-black object-contain" autoPlay playsInline muted />
      )}
      {error && <p role="alert" className="rounded-lg bg-rose-950 p-3 text-sm text-rose-100">{error}</p>}
      <div className="flex flex-wrap gap-2">
        {!cameraStarted && !photo && <button onClick={startCamera} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold">Start camera</button>}
        {cameraStarted && !photo && <button onClick={capture} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold">Capture</button>}
        {photo && <>
          <button onClick={() => setPhoto('')} className="inline-flex items-center gap-2 rounded-lg bg-stone-700 px-4 py-2 text-sm"><RotateCcw className="w-4 h-4" />Retake</button>
          <button onClick={usePhoto} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold"><Check className="w-4 h-4" />Use photo</button>
        </>}
        {!cameraStarted && error && <VideoOff className="h-5 w-5 text-stone-400" />}
      </div>
      <p className="text-xs text-stone-400">Camera access starts only when you select Start camera. Captures are uploaded only after you choose Use photo.</p>
    </div>
  );
}
