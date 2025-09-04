/**
 * Reports Service
 * 
 * Handles report generation, management, and sharing
 */

import { apiClient } from './base'
import {
  Report,
  ReportContent,
  ReportMetadata,
  ApiResponse,
  PaginatedResponse,
  RequestParams,
} from '../../types/api'

export interface CreateReportRequest {
  title: string
  type: 'stock' | 'portfolio' | 'market' | 'custom'
  symbol?: string
  portfolioId?: string
  template?: string
  parameters?: Record<string, any>
}

export interface UpdateReportRequest {
  title?: string
  content?: Partial<ReportContent>
  metadata?: Partial<ReportMetadata>
  status?: 'draft' | 'published' | 'archived'
}

export interface ReportTemplate {
  id: string
  name: string
  type: 'stock' | 'portfolio' | 'market' | 'custom'
  description: string
  sections: any[]
  charts: any[]
  parameters: any[]
  isPublic: boolean
  createdAt: string
  updatedAt: string
}

export interface ReportSchedule {
  id: string
  reportId: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  dayOfWeek?: number
  dayOfMonth?: number
  time: string
  timezone: string
  recipients: string[]
  isActive: boolean
  lastRun?: string
  nextRun: string
  createdAt: string
  updatedAt: string
}

export class ReportsService {
  private readonly basePath = '/reports'

  /**
   * Get all reports for the current user
   */
  async getReports(params: RequestParams = {}): Promise<PaginatedResponse<Report>> {
    const response = await apiClient.get<PaginatedResponse<Report>>(
      this.basePath,
      { params }
    )
    return response.data
  }

  /**
   * Get a specific report
   */
  async getReport(reportId: string): Promise<Report> {
    const response = await apiClient.get<Report>(`${this.basePath}/${reportId}`)
    return response.data
  }

  /**
   * Create a new report
   */
  async createReport(data: CreateReportRequest): Promise<Report> {
    const response = await apiClient.post<Report>(this.basePath, data)
    return response.data
  }

  /**
   * Update report
   */
  async updateReport(reportId: string, data: UpdateReportRequest): Promise<Report> {
    const response = await apiClient.patch<Report>(`${this.basePath}/${reportId}`, data)
    return response.data
  }

  /**
   * Delete report
   */
  async deleteReport(reportId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${reportId}`)
  }

  /**
   * Duplicate report
   */
  async duplicateReport(reportId: string, title: string): Promise<Report> {
    const response = await apiClient.post<Report>(
      `${this.basePath}/${reportId}/duplicate`,
      { title }
    )
    return response.data
  }

  /**
   * Generate report content
   */
  async generateReport(reportId: string, parameters?: Record<string, any>): Promise<Report> {
    const response = await apiClient.post<Report>(
      `${this.basePath}/${reportId}/generate`,
      { parameters }
    )
    return response.data
  }

  /**
   * Export report
   */
  async exportReport(
    reportId: string,
    format: 'pdf' | 'html' | 'docx' | 'xlsx' = 'pdf'
  ): Promise<Blob> {
    const response = await apiClient.get(
      `${this.basePath}/${reportId}/export`,
      { params: { format } }
    )
    return response.data
  }

  /**
   * Share report
   */
  async shareReport(
    reportId: string,
    options: {
      recipients: string[]
      message?: string
      expiresAt?: string
      allowDownload?: boolean
    }
  ): Promise<{ shareUrl: string; expiresAt: string }> {
    const response = await apiClient.post(
      `${this.basePath}/${reportId}/share`,
      options
    )
    return response.data
  }

  /**
   * Get shared report (public access)
   */
  async getSharedReport(shareToken: string): Promise<Report> {
    const response = await apiClient.get<Report>(
      `${this.basePath}/shared/${shareToken}`,
      { skipAuth: true }
    )
    return response.data
  }

  /**
   * Get report templates
   */
  async getTemplates(type?: string): Promise<ReportTemplate[]> {
    const params: any = {}
    if (type) params.type = type
    
    const response = await apiClient.get<ReportTemplate[]>(
      `${this.basePath}/templates`,
      { params }
    )
    return response.data
  }

  /**
   * Get report template
   */
  async getTemplate(templateId: string): Promise<ReportTemplate> {
    const response = await apiClient.get<ReportTemplate>(
      `${this.basePath}/templates/${templateId}`
    )
    return response.data
  }

  /**
   * Create report from template
   */
  async createFromTemplate(
    templateId: string,
    data: Omit<CreateReportRequest, 'template'>
  ): Promise<Report> {
    const response = await apiClient.post<Report>(
      `${this.basePath}/templates/${templateId}/create`,
      data
    )
    return response.data
  }

  /**
   * Save report as template
   */
  async saveAsTemplate(
    reportId: string,
    name: string,
    description: string,
    isPublic: boolean = false
  ): Promise<ReportTemplate> {
    const response = await apiClient.post<ReportTemplate>(
      `${this.basePath}/${reportId}/save-as-template`,
      { name, description, isPublic }
    )
    return response.data
  }

  /**
   * Get report schedules
   */
  async getSchedules(reportId?: string): Promise<ReportSchedule[]> {
    const params: any = {}
    if (reportId) params.reportId = reportId
    
    const response = await apiClient.get<ReportSchedule[]>(
      `${this.basePath}/schedules`,
      { params }
    )
    return response.data
  }

  /**
   * Create report schedule
   */
  async createSchedule(
    reportId: string,
    schedule: Omit<ReportSchedule, 'id' | 'reportId' | 'createdAt' | 'updatedAt'>
  ): Promise<ReportSchedule> {
    const response = await apiClient.post<ReportSchedule>(
      `${this.basePath}/schedules`,
      { reportId, ...schedule }
    )
    return response.data
  }

  /**
   * Update report schedule
   */
  async updateSchedule(
    scheduleId: string,
    data: Partial<Omit<ReportSchedule, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<ReportSchedule> {
    const response = await apiClient.patch<ReportSchedule>(
      `${this.basePath}/schedules/${scheduleId}`,
      data
    )
    return response.data
  }

  /**
   * Delete report schedule
   */
  async deleteSchedule(scheduleId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/schedules/${scheduleId}`)
  }

  /**
   * Get report history
   */
  async getReportHistory(
    reportId: string,
    params: RequestParams = {}
  ): Promise<PaginatedResponse<any>> {
    const response = await apiClient.get<PaginatedResponse<any>>(
      `${this.basePath}/${reportId}/history`,
      { params }
    )
    return response.data
  }

  /**
   * Get report analytics
   */
  async getReportAnalytics(reportId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/analytics`)
    return response.data
  }

  /**
   * Get report comments
   */
  async getComments(reportId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/comments`)
    return response.data
  }

  /**
   * Add comment to report
   */
  async addComment(reportId: string, comment: string): Promise<any> {
    const response = await apiClient.post(`${this.basePath}/${reportId}/comments`, {
      comment,
    })
    return response.data
  }

  /**
   * Update comment
   */
  async updateComment(reportId: string, commentId: string, comment: string): Promise<any> {
    const response = await apiClient.patch(
      `${this.basePath}/${reportId}/comments/${commentId}`,
      { comment }
    )
    return response.data
  }

  /**
   * Delete comment
   */
  async deleteComment(reportId: string, commentId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${reportId}/comments/${commentId}`)
  }

  /**
   * Get report tags
   */
  async getTags(): Promise<string[]> {
    const response = await apiClient.get<string[]>(`${this.basePath}/tags`)
    return response.data
  }

  /**
   * Add tags to report
   */
  async addTags(reportId: string, tags: string[]): Promise<void> {
    await apiClient.patch(`${this.basePath}/${reportId}/tags`, { tags })
  }

  /**
   * Remove tags from report
   */
  async removeTags(reportId: string, tags: string[]): Promise<void> {
    await apiClient.delete(`${this.basePath}/${reportId}/tags`, {
      body: JSON.stringify({ tags }),
    })
  }

  /**
   * Get report favorites
   */
  async getFavorites(): Promise<Report[]> {
    const response = await apiClient.get<Report[]>(`${this.basePath}/favorites`)
    return response.data
  }

  /**
   * Add report to favorites
   */
  async addToFavorites(reportId: string): Promise<void> {
    await apiClient.post(`${this.basePath}/${reportId}/favorite`)
  }

  /**
   * Remove report from favorites
   */
  async removeFromFavorites(reportId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${reportId}/favorite`)
  }

  /**
   * Get report collaborators
   */
  async getCollaborators(reportId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/collaborators`)
    return response.data
  }

  /**
   * Add collaborator to report
   */
  async addCollaborator(reportId: string, email: string, role: 'viewer' | 'editor'): Promise<void> {
    await apiClient.post(`${this.basePath}/${reportId}/collaborators`, {
      email,
      role,
    })
  }

  /**
   * Update collaborator role
   */
  async updateCollaborator(
    reportId: string,
    userId: string,
    role: 'viewer' | 'editor'
  ): Promise<void> {
    await apiClient.patch(`${this.basePath}/${reportId}/collaborators/${userId}`, {
      role,
    })
  }

  /**
   * Remove collaborator from report
   */
  async removeCollaborator(reportId: string, userId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${reportId}/collaborators/${userId}`)
  }

  /**
   * Get report versions
   */
  async getVersions(reportId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/versions`)
    return response.data
  }

  /**
   * Restore report version
   */
  async restoreVersion(reportId: string, versionId: string): Promise<Report> {
    const response = await apiClient.post<Report>(
      `${this.basePath}/${reportId}/versions/${versionId}/restore`
    )
    return response.data
  }

  /**
   * Get report insights
   */
  async getInsights(reportId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/insights`)
    return response.data
  }

  /**
   * Get report performance metrics
   */
  async getPerformanceMetrics(reportId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${reportId}/performance`)
    return response.data
  }
}

// Create singleton instance
export const reportsService = new ReportsService()
