/**
 * TypeScript mirror of packages/contracts canonical schemas
 */

export interface StandardResponse<T> {
  success: boolean
  data?: T
  message?: string
  correlation_id?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HealthStatus {
  status: string
  version: string
  environment: string
  timestamp: string
  uptime_seconds: number
}

export interface ResourceItem {
  id: string
  name: string
  description: string
  status: string
}
