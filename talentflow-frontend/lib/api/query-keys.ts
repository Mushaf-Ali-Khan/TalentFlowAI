export const queryKeys = {
  jobs: {
    all:    ()    => ['jobs'] as const,
    list:   (filters?: any) => ['jobs', 'list', filters] as const,
    detail: (id: string)  => ['jobs', 'detail', id] as const,
  },
  pipeline: {
    batch:  (batchId: string) => ['pipeline', 'batch', batchId] as const,
  },
  candidates: {
    all:    ()    => ['candidates'] as const,
    list:   (filters?: any) => ['candidates', 'list', filters] as const,
    detail: (id: string)  => ['candidates', 'detail', id] as const,
  },
  shortlists: {
    batch:  (batchId: string) => ['shortlists', batchId] as const,
  },
  analytics: {
    overview: () => ['analytics', 'overview'] as const,
    bias:     () => ['analytics', 'bias'] as const,
  },
}
