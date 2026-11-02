import React, { useRef, useState, useEffect } from 'react';
import { Upload, Image as ImageIcon, Trash2, RefreshCw, AlertCircle } from 'lucide-react';

export default function UploadArea({
  selectedFile,
  previewUrl,
  onFileSelect,
  onFileRemove,
  error,
  setError
}) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const validateAndProcessFile = (file) => {
    if (!file) return;

    setError('');

    // File type validation
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a JPG or PNG image.');
      return;
    }

    // File size validation (10MB)
    const maxSizeInBytes = 10 * 1024 * 1024;
    if (file.size > maxSizeInBytes) {
      setError('Image must be smaller than 10MB.');
      return;
    }

    onFileSelect(file);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };


  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      {/* Hidden native file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept="image/jpeg,image/png,image/jpg"
        className="hidden"
      />

      {/* Image Preview Container or Dropzone */}
      {previewUrl ? (
        <div className="relative rounded-2xl border border-stone-200 bg-white p-3 shadow-xs space-y-3">
          {/* Main Image Frame */}
          <div className="relative rounded-xl overflow-hidden bg-stone-100 flex items-center justify-center min-h-[300px] max-h-[420px]">
            <img
              src={previewUrl}
              alt="Selected produce preview"
              className="w-full h-full object-contain max-h-[400px] rounded-xl"
            />

            {/* Bottom Overlay Bar */}
            <div className="absolute bottom-2 left-2 right-2 px-3 py-2 rounded-lg bg-neutral-900/85 backdrop-blur-xs text-white flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 truncate pr-2">
                <ImageIcon className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="truncate font-mono font-medium text-[11px]">
                  {selectedFile?.name || 'produce_image.jpg'}
                </span>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-stone-800 hover:bg-stone-700 text-stone-200 font-semibold text-[11px] transition-colors"
                >
                  <RefreshCw className="w-3 h-3 text-emerald-400" />
                  <span>Change</span>
                </button>

                <button
                  type="button"
                  onClick={onFileRemove}
                  className="p-1 rounded bg-stone-800 hover:bg-rose-900/80 text-stone-300 hover:text-white transition-colors"
                  aria-label="Remove image"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Dropzone Box */
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}

          className={`rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center cursor-pointer transition-all duration-150 flex flex-col items-center justify-center min-h-[320px] sm:min-h-[380px] ${
            isDragging
              ? 'border-emerald-600 bg-emerald-50/60'
              : 'border-stone-300 bg-white hover:border-emerald-500 hover:bg-stone-50/80'
          }`}
        >
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200/80 flex items-center justify-center text-emerald-700 mb-4 shadow-2xs">
            <Upload className="w-7 h-7" />
          </div>

          <h4 className="text-base sm:text-lg font-bold text-neutral-900 tracking-tight mb-1">
            {isDragging ? 'Drop image to analyze' : 'Drop your produce image here'}
          </h4>

          <p className="text-xs sm:text-sm text-stone-600 font-medium mb-3">
            or <span className="text-emerald-700 font-semibold underline underline-offset-2">click to browse</span>
          </p>

          <span className="text-[11px] font-mono text-stone-400 px-3 py-1 bg-stone-100 rounded-md border border-stone-200/60">
            JPG, JPEG or PNG • Max 10MB
          </span>
        </div>
      )}

      {/* Inline Error Message */}
      {error && (
        <div className="mt-3 flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
