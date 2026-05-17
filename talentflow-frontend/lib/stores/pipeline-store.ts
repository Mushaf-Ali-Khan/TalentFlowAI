import { create } from 'zustand'

export type UploadState = 'idle' | 'uploading' | 'processing' | 'done' | 'error'

export interface StagedFile {
  id: string
  file: File
  progress: number
  status: UploadState
  error?: string
  r2Key?: string
}

interface PipelineState {
  stagedFiles: StagedFile[]
  addFiles: (files: File[]) => void
  removeFile: (id: string) => void
  updateFileProgress: (id: string, progress: number) => void
  updateFileStatus: (id: string, status: UploadState, error?: string, r2Key?: string) => void
  clearFiles: () => void
  batchId: string | null
  setBatchId: (id: string | null) => void
}

export const usePipelineStore = create<PipelineState>((set) => ({
  stagedFiles: [],
  addFiles: (files) => set((state) => {
    const newStaged = files.map(f => ({
      id: crypto.randomUUID(),
      file: f,
      progress: 0,
      status: 'idle' as UploadState
    }))
    return { stagedFiles: [...state.stagedFiles, ...newStaged] }
  }),
  removeFile: (id) => set((state) => ({
    stagedFiles: state.stagedFiles.filter(f => f.id !== id)
  })),
  updateFileProgress: (id, progress) => set((state) => ({
    stagedFiles: state.stagedFiles.map(f => f.id === id ? { ...f, progress } : f)
  })),
  updateFileStatus: (id, status, error, r2Key) => set((state) => ({
    stagedFiles: state.stagedFiles.map(f => f.id === id ? { ...f, status, error, r2Key: r2Key || f.r2Key } : f)
  })),
  clearFiles: () => set({ stagedFiles: [] }),
  batchId: null,
  setBatchId: (id) => set({ batchId: id })
}))
