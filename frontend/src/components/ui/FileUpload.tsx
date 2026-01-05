import { useState, useCallback } from 'react';
import { Upload, File, X, Check } from 'lucide-react';
import clsx from 'clsx';

interface FileUploadProps {
  onFilesChange?: (files: File[]) => void;
  multiple?: boolean;
  accept?: string;
  maxSize?: number; // in bytes
  className?: string;
  compact?: boolean;
}

interface UploadedFile {
  file: File;
  id: string;
  status: 'uploading' | 'success' | 'error';
}

export default function FileUpload({
  onFilesChange,
  multiple = true,
  accept = '.pdf,.doc,.docx,.xlsx,.xls,.csv',
  maxSize = 10 * 1024 * 1024, // 10MB
  className,
  compact = false,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      const droppedFiles = Array.from(e.dataTransfer.files);
      processFiles(droppedFiles);
    },
    [onFilesChange]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      processFiles(selectedFiles);
    }
  };

  const processFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter((file) => file.size <= maxSize);
    const uploadedFiles: UploadedFile[] = validFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'success' as const,
    }));

    setFiles((prev) => (multiple ? [...prev, ...uploadedFiles] : uploadedFiles));
    onFilesChange?.(validFiles);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  if (compact) {
    return (
      <label className="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 text-sm text-purple-brand hover:text-purple-deep border border-purple-brand/30 rounded-lg hover:bg-purple-50 transition-colors">
        <Upload size={16} />
        <span>Upload</span>
        <input
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />
      </label>
    );
  }

  return (
    <div className={clsx('space-y-4', className)}>
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={clsx(
          'relative border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          dragActive
            ? 'border-purple-brand bg-purple-50'
            : 'border-gray-300 hover:border-purple-brand/50'
        )}
      >
        <input
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center gap-2">
          <div className="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center">
            <Upload className="text-purple-brand" size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700">
              <span className="text-purple-brand">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500 mt-1">
              PDF, DOC, XLSX up to {maxSize / 1024 / 1024}MB
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((uploadedFile) => (
            <div
              key={uploadedFile.id}
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
            >
              <File size={20} className="text-gray-400" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-700 truncate">
                  {uploadedFile.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(uploadedFile.file.size / 1024).toFixed(1)} KB
                </p>
              </div>
              {uploadedFile.status === 'success' && (
                <Check size={18} className="text-green-500" />
              )}
              <button
                onClick={() => removeFile(uploadedFile.id)}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <X size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
