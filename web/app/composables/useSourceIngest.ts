/**
 * Source ingestion: presigned upload → PUT to S3 → confirm. Returns job id for streaming.
 */
import { ref } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type {
  ConfirmUploadRequest,
  ConfirmUploadResponse,
  JobStatus,
  PresignedUploadRequest,
  PresignedUploadResponse,
  Source,
  SourceListResponse,
  SourceVersion,
} from '@@/types/api'

export function useSourceList() {
  return useQuery({
    queryKey: ['sources'],
    queryFn: () => apiClient<SourceListResponse>('/sources'),
  })
}

export function useSource(id: string) {
  return useQuery({
    queryKey: ['source', id],
    enabled: () => !!id,
    queryFn: () => apiClient<Source>(`/sources/${id}`),
  })
}

export function useSourceVersions(id: string) {
  return useQuery({
    queryKey: ['source', id, 'versions'],
    enabled: () => !!id,
    queryFn: () => apiClient<SourceVersion[]>(`/sources/${id}/versions`),
  })
}

export function useSourceJobs(id: string) {
  return useQuery({
    queryKey: ['source', id, 'jobs'],
    enabled: () => !!id,
    queryFn: () => apiClient<JobStatus[]>(`/sources/${id}/jobs`),
  })
}

export function useSourceIngest() {
  const qc = useQueryClient()
  const progress = ref(0)

  const ingest = async (file: File, meta: Omit<PresignedUploadRequest, 'source_type'>) => {
    progress.value = 0
    const presigned = await apiClient<PresignedUploadResponse>('/sources/presigned', {
      method: 'POST',
      body: {
        source_type: inferType(file),
        title: meta.title || file.name,
        pipeline_id: meta.pipeline_id ?? 'default_pdf_pipeline',
        metadata: meta.metadata ?? {},
      } satisfies PresignedUploadRequest,
    })

    await uploadToPresigned(presigned.upload_url, file, (pct) => (progress.value = pct))

    const confirm = await apiClient<ConfirmUploadResponse>('/sources/confirm', {
      method: 'POST',
      body: {
        source_id: presigned.source_id,
        version_id: presigned.version_id,
      } satisfies ConfirmUploadRequest,
    })

    qc.invalidateQueries({ queryKey: ['sources'] })
    return { ...presigned, ...confirm }
  }

  return { ingest, progress }
}

function inferType(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  if (ext === 'pdf') return 'pdf'
  if (['md', 'markdown'].includes(ext)) return 'md'
  if (['txt', 'text'].includes(ext)) return 'txt'
  return 'file'
}

function uploadToPresigned(url: string, file: File, onProgress: (pct: number) => void) {
  return new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', url)
    xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream')
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress((e.loaded / e.total) * 100)
    }
    xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed: ${xhr.status}`)))
    xhr.onerror = () => reject(new Error('Network error during upload'))
    xhr.send(file)
  })
}

export function useCreateUrlSource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: { url: string; title?: string }) =>
      apiClient('/sources', {
        method: 'POST',
        body: {
          source_type: 'url',
          title: input.title || input.url,
          uri: input.url,
          metadata: {},
        },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  })
}
