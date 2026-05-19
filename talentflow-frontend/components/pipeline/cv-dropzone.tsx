'use client'

import { useCallback, useState } from 'react'
import { UploadCloud, File, X, AlertCircle, CheckCircle2 } from 'lucide-react'
import { usePipelineStore } from '@/lib/stores/pipeline-store'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function CVDropzone() {
  const [isDragging, setIsDragging] = useState(false)
  const addFiles = usePipelineStore((state) => state.addFiles)
  const stagedFiles = usePipelineStore((state) => state.stagedFiles)
  const removeFile = usePipelineStore((state) => state.removeFile)

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files))
    }
  }, [addFiles])

  const onFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      addFiles(Array.from(e.target.files))
    }
  }, [addFiles])

  return (
    <div className="w-full space-y-4">
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={cn(
          "border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center transition-colors text-center cursor-pointer bg-white/80",
          isDragging ? "border-[var(--tf-accent)] bg-emerald-50" : "border-[var(--tf-border)] hover:border-[var(--tf-accent-3)]"
        )}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <UploadCloud className="w-12 h-12 text-[var(--tf-muted)] mb-4" />
        <h3 className="text-lg font-semibold text-[var(--tf-ink)]">Drag & drop candidate CVs</h3>
        <p className="text-sm text-[var(--tf-muted)] mt-1">Supports PDF and DOCX up to 10MB</p>
        <input
          id="file-upload"
          type="file"
          multiple
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={onFileInput}
        />
        <button className="mt-6 px-4 py-2 bg-[var(--tf-accent)] text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors">
          Browse Files
        </button>
      </div>

      {stagedFiles.length > 0 && (
        <div className="bg-white/90 border border-[var(--tf-border)] rounded-xl overflow-hidden shadow-sm">
          <div className="px-4 py-3 border-b border-[var(--tf-border)] bg-white/70 flex justify-between items-center">
            <h4 className="font-medium text-[var(--tf-ink)]">Staged Files ({stagedFiles.length})</h4>
          </div>
          <ul className="divide-y max-h-60 overflow-y-auto">
            {stagedFiles.map((f) => (
              <li key={f.id} className="p-3 flex items-center justify-between hover:bg-[var(--tf-surface-2)]">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <File className="w-5 h-5 text-[var(--tf-muted)] flex-shrink-0" />
                  <span className="text-sm font-medium text-[var(--tf-ink)] truncate">{f.file.name}</span>
                  <span className="text-xs text-[var(--tf-muted)] flex-shrink-0">
                    {(f.file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                <div className="flex items-center space-x-3 pl-2">
                  {f.status === 'uploading' && (
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div className="bg-[var(--tf-accent)] h-2 rounded-full" style={{ width: `${f.progress}%` }}></div>
                    </div>
                  )}
                  {f.status === 'done' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                  {f.status === 'error' && <AlertCircle className="w-5 h-5 text-red-500" title={f.error} />}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(f.id)
                    }}
                    className="p-1 rounded-md text-[var(--tf-muted)] hover:text-red-500 hover:bg-red-50 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
