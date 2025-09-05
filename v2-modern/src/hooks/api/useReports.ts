/**
 * Reports Hooks
 * 
 * React Query hooks for report management operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reportsService } from '../../services/api/reports'
import { Report, ReportTemplate, ReportSchedule } from '../../types/api'

// Query Keys
export const reportKeys = {
  all: ['reports'] as const,
  lists: () => [...reportKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...reportKeys.lists(), filters] as const,
  details: () => [...reportKeys.all, 'detail'] as const,
  detail: (id: string) => [...reportKeys.details(), id] as const,
  templates: () => [...reportKeys.all, 'templates'] as const,
  template: (id: string) => [...reportKeys.templates(), id] as const,
  schedules: () => [...reportKeys.all, 'schedules'] as const,
  schedule: (id: string) => [...reportKeys.schedules(), id] as const,
  history: (id: string, params: Record<string, any>) => 
    [...reportKeys.detail(id), 'history', params] as const,
  comments: (id: string) => [...reportKeys.detail(id), 'comments'] as const,
  collaborators: (id: string) => [...reportKeys.detail(id), 'collaborators'] as const,
  versions: (id: string) => [...reportKeys.detail(id), 'versions'] as const,
  favorites: () => [...reportKeys.all, 'favorites'] as const,
  tags: () => [...reportKeys.all, 'tags'] as const,
}

// Get all reports
export const useReports = (params: Record<string, any> = {}) => {
  return useQuery({
    queryKey: reportKeys.list(params),
    queryFn: () => reportsService.getReports(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report
export const useReport = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: reportKeys.detail(reportId),
    queryFn: () => reportsService.getReport(reportId),
    enabled: enabled && !!reportId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report templates
export const useReportTemplates = (type?: string) => {
  return useQuery({
    queryKey: type ? [...reportKeys.templates(), type] : reportKeys.templates(),
    queryFn: () => reportsService.getTemplates(type),
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get report template
export const useReportTemplate = (templateId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: reportKeys.template(templateId),
    queryFn: () => reportsService.getTemplate(templateId),
    enabled: enabled && !!templateId,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get report schedules
export const useReportSchedules = (reportId?: string) => {
  return useQuery({
    queryKey: reportId ? [...reportKeys.schedules(), reportId] : reportKeys.schedules(),
    queryFn: () => reportsService.getSchedules(reportId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report history
export const useReportHistory = (
  reportId: string,
  params: Record<string, any> = {},
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: reportKeys.history(reportId, params),
    queryFn: () => reportsService.getReportHistory(reportId, params),
    enabled: enabled && !!reportId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report comments
export const useReportComments = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: reportKeys.comments(reportId),
    queryFn: () => reportsService.getComments(reportId),
    enabled: enabled && !!reportId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get report collaborators
export const useReportCollaborators = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: reportKeys.collaborators(reportId),
    queryFn: () => reportsService.getCollaborators(reportId),
    enabled: enabled && !!reportId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report versions
export const useReportVersions = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: reportKeys.versions(reportId),
    queryFn: () => reportsService.getVersions(reportId),
    enabled: enabled && !!reportId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get favorite reports
export const useFavoriteReports = () => {
  return useQuery({
    queryKey: reportKeys.favorites(),
    queryFn: reportsService.getFavorites,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get report tags
export const useReportTags = () => {
  return useQuery({
    queryKey: reportKeys.tags(),
    queryFn: reportsService.getTags,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Create report mutation
export const useCreateReport = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: reportsService.createReport,
    onSuccess: () => {
      // Invalidate reports list
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to create report:', error)
    },
  })
}

// Update report mutation
export const useUpdateReport = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, data }: { reportId: string; data: any }) =>
      reportsService.updateReport(reportId, data),
    onSuccess: (data, { reportId }) => {
      // Update report in cache
      queryClient.setQueryData(reportKeys.detail(reportId), data)
      // Invalidate reports list
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to update report:', error)
    },
  })
}

// Delete report mutation
export const useDeleteReport = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: reportsService.deleteReport,
    onSuccess: (_, reportId) => {
      // Remove report from cache
      queryClient.removeQueries({ queryKey: reportKeys.detail(reportId) })
      // Invalidate reports list
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to delete report:', error)
    },
  })
}

// Duplicate report mutation
export const useDuplicateReport = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, title }: { reportId: string; title: string }) =>
      reportsService.duplicateReport(reportId, title),
    onSuccess: () => {
      // Invalidate reports list
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to duplicate report:', error)
    },
  })
}

// Generate report mutation
export const useGenerateReport = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, parameters }: { reportId: string; parameters?: Record<string, any> }) =>
      reportsService.generateReport(reportId, parameters),
    onSuccess: (data, { reportId }) => {
      // Update report in cache
      queryClient.setQueryData(reportKeys.detail(reportId), data)
    },
    onError: (error) => {
      console.error('Failed to generate report:', error)
    },
  })
}

// Export report mutation
export const useExportReport = () => {
  return useMutation({
    mutationFn: ({ reportId, format }: { reportId: string; format: 'pdf' | 'html' | 'docx' | 'xlsx' }) =>
      reportsService.exportReport(reportId, format),
    onError: (error) => {
      console.error('Failed to export report:', error)
    },
  })
}

// Share report mutation
export const useShareReport = () => {
  return useMutation({
    mutationFn: ({ reportId, options }: { reportId: string; options: any }) =>
      reportsService.shareReport(reportId, options),
    onError: (error) => {
      console.error('Failed to share report:', error)
    },
  })
}

// Create from template mutation
export const useCreateFromTemplate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ templateId, data }: { templateId: string; data: any }) =>
      reportsService.createFromTemplate(templateId, data),
    onSuccess: () => {
      // Invalidate reports list
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to create report from template:', error)
    },
  })
}

// Save as template mutation
export const useSaveAsTemplate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, name, description, isPublic }: { 
      reportId: string; 
      name: string; 
      description: string; 
      isPublic: boolean 
    }) => reportsService.saveAsTemplate(reportId, name, description, isPublic),
    onSuccess: () => {
      // Invalidate templates
      queryClient.invalidateQueries({ queryKey: reportKeys.templates() })
    },
    onError: (error) => {
      console.error('Failed to save report as template:', error)
    },
  })
}

// Create schedule mutation
export const useCreateReportSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, schedule }: { reportId: string; schedule: any }) =>
      reportsService.createSchedule(reportId, schedule),
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
    onError: (error) => {
      console.error('Failed to create report schedule:', error)
    },
  })
}

// Update schedule mutation
export const useUpdateReportSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ scheduleId, data }: { scheduleId: string; data: any }) =>
      reportsService.updateSchedule(scheduleId, data),
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
    onError: (error) => {
      console.error('Failed to update report schedule:', error)
    },
  })
}

// Delete schedule mutation
export const useDeleteReportSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: reportsService.deleteSchedule,
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
    onError: (error) => {
      console.error('Failed to delete report schedule:', error)
    },
  })
}

// Add comment mutation
export const useAddReportComment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, comment }: { reportId: string; comment: string }) =>
      reportsService.addComment(reportId, comment),
    onSuccess: (_, { reportId }) => {
      // Invalidate comments
      queryClient.invalidateQueries({ queryKey: reportKeys.comments(reportId) })
    },
    onError: (error) => {
      console.error('Failed to add comment:', error)
    },
  })
}

// Update comment mutation
export const useUpdateReportComment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, commentId, comment }: { reportId: string; commentId: string; comment: string }) =>
      reportsService.updateComment(reportId, commentId, comment),
    onSuccess: (_, { reportId }) => {
      // Invalidate comments
      queryClient.invalidateQueries({ queryKey: reportKeys.comments(reportId) })
    },
    onError: (error) => {
      console.error('Failed to update comment:', error)
    },
  })
}

// Delete comment mutation
export const useDeleteReportComment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, commentId }: { reportId: string; commentId: string }) =>
      reportsService.deleteComment(reportId, commentId),
    onSuccess: (_, { reportId }) => {
      // Invalidate comments
      queryClient.invalidateQueries({ queryKey: reportKeys.comments(reportId) })
    },
    onError: (error) => {
      console.error('Failed to delete comment:', error)
    },
  })
}

// Add to favorites mutation
export const useAddToFavorites = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: reportsService.addToFavorites,
    onSuccess: () => {
      // Invalidate favorites
      queryClient.invalidateQueries({ queryKey: reportKeys.favorites() })
    },
    onError: (error) => {
      console.error('Failed to add to favorites:', error)
    },
  })
}

// Remove from favorites mutation
export const useRemoveFromFavorites = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: reportsService.removeFromFavorites,
    onSuccess: () => {
      // Invalidate favorites
      queryClient.invalidateQueries({ queryKey: reportKeys.favorites() })
    },
    onError: (error) => {
      console.error('Failed to remove from favorites:', error)
    },
  })
}

// Add collaborator mutation
export const useAddCollaborator = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, email, role }: { reportId: string; email: string; role: 'viewer' | 'editor' }) =>
      reportsService.addCollaborator(reportId, email, role),
    onSuccess: (_, { reportId }) => {
      // Invalidate collaborators
      queryClient.invalidateQueries({ queryKey: reportKeys.collaborators(reportId) })
    },
    onError: (error) => {
      console.error('Failed to add collaborator:', error)
    },
  })
}

// Update collaborator mutation
export const useUpdateCollaborator = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, userId, role }: { reportId: string; userId: string; role: 'viewer' | 'editor' }) =>
      reportsService.updateCollaborator(reportId, userId, role),
    onSuccess: (_, { reportId }) => {
      // Invalidate collaborators
      queryClient.invalidateQueries({ queryKey: reportKeys.collaborators(reportId) })
    },
    onError: (error) => {
      console.error('Failed to update collaborator:', error)
    },
  })
}

// Remove collaborator mutation
export const useRemoveCollaborator = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, userId }: { reportId: string; userId: string }) =>
      reportsService.removeCollaborator(reportId, userId),
    onSuccess: (_, { reportId }) => {
      // Invalidate collaborators
      queryClient.invalidateQueries({ queryKey: reportKeys.collaborators(reportId) })
    },
    onError: (error) => {
      console.error('Failed to remove collaborator:', error)
    },
  })
}

// Restore version mutation
export const useRestoreReportVersion = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reportId, versionId }: { reportId: string; versionId: string }) =>
      reportsService.restoreVersion(reportId, versionId),
    onSuccess: (data, { reportId }) => {
      // Update report in cache
      queryClient.setQueryData(reportKeys.detail(reportId), data)
      // Invalidate versions
      queryClient.invalidateQueries({ queryKey: reportKeys.versions(reportId) })
    },
    onError: (error) => {
      console.error('Failed to restore report version:', error)
    },
  })
}

// Get report insights
export const useReportInsights = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...reportKeys.detail(reportId), 'insights'],
    queryFn: () => reportsService.getInsights(reportId),
    enabled: enabled && !!reportId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get report performance metrics
export const useReportPerformanceMetrics = (reportId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...reportKeys.detail(reportId), 'performance'],
    queryFn: () => reportsService.getPerformanceMetrics(reportId),
    enabled: enabled && !!reportId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}
