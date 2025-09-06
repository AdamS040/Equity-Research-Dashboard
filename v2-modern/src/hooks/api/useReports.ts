import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../../services/api'

// Types
export interface Report {
  id: string
  title: string
  description: string
  type: string
  status: 'draft' | 'generating' | 'completed' | 'failed'
  content: any
  tags: string[]
  created_at: string
  updated_at: string
  created_by: string
  view_count: number
  export_count: number
  share_count: number
}

export interface CreateReportRequest {
  title: string
  description?: string
  type: string
  content?: any
  tags?: string[]
}

export interface UpdateReportRequest {
  reportId: string
  updates: Partial<CreateReportRequest>
}

export interface ReportExportRequest {
  reportId: string
  format: 'pdf' | 'excel' | 'html' | 'image' | 'csv'
  options?: {
    includeCharts?: boolean
    includeTables?: boolean
    includeMetadata?: boolean
    quality?: string
    pageSize?: string
    orientation?: string
  }
}

export interface ReportShareRequest {
  reportId: string
  permissions: 'view' | 'edit' | 'admin'
  expires_at?: string
  password?: string
}

// Query Keys
export const reportKeys = {
  all: ['reports'] as const,
  lists: () => [...reportKeys.all, 'list'] as const,
  list: (filters: any) => [...reportKeys.lists(), { filters }] as const,
  details: () => [...reportKeys.all, 'detail'] as const,
  detail: (id: string) => [...reportKeys.details(), id] as const,
  exports: () => [...reportKeys.all, 'exports'] as const,
  shares: () => [...reportKeys.all, 'shares'] as const,
  templates: () => [...reportKeys.all, 'templates'] as const,
  scheduled: () => [...reportKeys.all, 'scheduled'] as const
}

// Hooks
export const useReports = (filters?: {
  type?: string
  status?: string
  search?: string
  page?: number
  limit?: number
}) => {
  return useQuery({
    queryKey: reportKeys.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.type) params.append('type', filters.type)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.search) params.append('search', filters.search)
      if (filters?.page) params.append('page', filters.page.toString())
      if (filters?.limit) params.append('limit', filters.limit.toString())
      
      const response = await apiClient.get(`/reports?${params.toString()}`)
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useReport = (reportId: string) => {
  return useQuery({
    queryKey: reportKeys.detail(reportId),
    queryFn: async () => {
      const response = await apiClient.get(`/reports/${reportId}`)
      return response.data
    },
    enabled: !!reportId,
    staleTime: 5 * 60 * 1000,
  })
}

export const useCreateReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: CreateReportRequest) => {
      const response = await apiClient.post('/reports', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
  })
}

export const useUpdateReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ reportId, updates }: UpdateReportRequest) => {
      const response = await apiClient.put(`/reports/${reportId}`, updates)
      return response.data
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
      queryClient.invalidateQueries({ queryKey: reportKeys.detail(variables.reportId) })
    },
  })
}

export const useDeleteReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (reportId: string) => {
      await apiClient.delete(`/reports/${reportId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
  })
}

export const useExportReport = () => {
  return useMutation({
    mutationFn: async ({ reportId, format, options }: ReportExportRequest) => {
      const response = await apiClient.post(`/reports/${reportId}/export`, {
        format,
        options
      }, {
        responseType: 'blob'
      })
      return response.data
    },
  })
}

export const useShareReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ reportId, permissions, expires_at, password }: ReportShareRequest) => {
      const response = await apiClient.post(`/reports/${reportId}/share`, {
        permissions,
        expires_at,
        password
      })
      return response.data
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: reportKeys.detail(variables.reportId) })
      queryClient.invalidateQueries({ queryKey: reportKeys.shares() })
    },
  })
}

export const useReportTemplates = () => {
  return useQuery({
    queryKey: reportKeys.templates(),
    queryFn: async () => {
      const response = await apiClient.get('/reports/templates')
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useScheduledReports = () => {
  return useQuery({
    queryKey: reportKeys.scheduled(),
    queryFn: async () => {
      const response = await apiClient.get('/reports/scheduled')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export const useCreateScheduledReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: {
      reportId: string
      schedule: string
      recipients: string[]
      format: string
      enabled: boolean
    }) => {
      const response = await apiClient.post('/reports/scheduled', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.scheduled() })
    },
  })
}

export const useUpdateScheduledReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      const response = await apiClient.put(`/reports/scheduled/${id}`, updates)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.scheduled() })
    },
  })
}

export const useDeleteScheduledReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/reports/scheduled/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.scheduled() })
    },
  })
}

// Utility hooks
export const useReportStats = () => {
  return useQuery({
    queryKey: [...reportKeys.all, 'stats'],
    queryFn: async () => {
      const response = await apiClient.get('/reports/stats')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export const useReportActivity = (reportId: string) => {
  return useQuery({
    queryKey: [...reportKeys.detail(reportId), 'activity'],
    queryFn: async () => {
      const response = await apiClient.get(`/reports/${reportId}/activity`)
      return response.data
    },
    enabled: !!reportId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}