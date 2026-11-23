import { StandardResponse, PaginatedResponse, ResourceItem, HealthStatus } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<StandardResponse<T>> {
    const headers = {
      'Content-Type': 'application/json',
      'X-Correlation-ID': crypto.randomUUID(),
      ...options.headers,
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null)
      throw new Error(errorBody?.message || `API error ${response.status}: ${response.statusText}`)
    }

    return response.json()
  }

  async getHealth(): Promise<StandardResponse<HealthStatus>> {
    return this.request<HealthStatus>('/api/v1/health/healthz')
  }

  async getResources(): Promise<StandardResponse<PaginatedResponse<ResourceItem>>> {
    return this.request<PaginatedResponse<ResourceItem>>('/api/v1/resources')
  }

  async createResource(name: string, description: string): Promise<StandardResponse<ResourceItem>> {
    return this.request<ResourceItem>('/api/v1/resources', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    })
  }
}

export const api = new ApiClient()
