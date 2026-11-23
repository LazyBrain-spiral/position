import React, { useEffect, useState } from 'react'
import { api } from './api/client'
import { HealthStatus, ResourceItem } from './types'

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const [healthRes, resourcesRes] = await Promise.all([
          api.getHealth().catch(() => null),
          api.getResources().catch(() => null),
        ])
        if (healthRes?.data) setHealth(healthRes.data)
        if (resourcesRes?.data?.items) setResources(resourcesRes.data.items)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    try {
      const res = await api.createResource(name, desc)
      if (res.data) {
        setResources(prev => [...prev, res.data!])
        setName('')
        setDesc('')
      }
    } catch (err) {
      alert(`Error creating item: ${(err as Error).message}`)
    }
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 20px' }}>
      <header style={{ borderBottom: '1px solid #1e293b', paddingBottom: 24, marginBottom: 32 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: 28, margin: 0, fontWeight: 700, color: '#38bdf8' }}>Enterprise SDE Platform</h1>
            <p style={{ color: '#94a3b8', margin: '6px 0 0' }}>Production Monorepo & 4-Track Engineering Architecture</p>
          </div>
          <div style={{ background: '#1e293b', padding: '10px 18px', borderRadius: 8, fontSize: 13, border: '1px solid #334155' }}>
            <span style={{ color: '#94a3b8' }}>API Status: </span>
            <strong style={{ color: health?.status === 'healthy' ? '#4ade80' : '#f87171' }}>
              {health?.status || 'Connecting...'}
            </strong>
            {health && <span style={{ marginLeft: 8, color: '#64748b' }}>v{health.version}</span>}
          </div>
        </div>
      </header>

      <main style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 32 }}>
        <section>
          <h2 style={{ fontSize: 18, color: '#f1f5f9', marginBottom: 16 }}>Active System Resources</h2>
          {loading ? (
            <div style={{ color: '#64748b' }}>Loading resources...</div>
          ) : (
            <div style={{ display: 'grid', gap: 14 }}>
              {resources.map(item => (
                <div
                  key={item.id}
                  style={{
                    background: '#131b2e',
                    border: '1px solid #1e293b',
                    borderRadius: 8,
                    padding: '16px 20px',
                    transition: 'border-color 0.2s',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ color: '#f8fafc', fontSize: 15 }}>{item.name}</strong>
                    <span style={{ fontSize: 12, background: '#0f172a', padding: '3px 8px', borderRadius: 4, color: '#38bdf8', border: '1px solid #1e293b' }}>
                      {item.id}
                    </span>
                  </div>
                  <p style={{ margin: '8px 0 0', color: '#94a3b8', fontSize: 14 }}>{item.description}</p>
                </div>
              ))}
            </div>
          )}
        </section>

        <aside>
          <div style={{ background: '#131b2e', border: '1px solid #1e293b', borderRadius: 8, padding: 20 }}>
            <h3 style={{ fontSize: 16, margin: '0 0 16px', color: '#f1f5f9' }}>Add Domain Resource</h3>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 6 }}>Resource Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="e.g. Ingestion Pipeline"
                  required
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: '#090d16',
                    border: '1px solid #334155',
                    borderRadius: 6,
                    color: '#fff',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 6 }}>Description</label>
                <textarea
                  value={desc}
                  onChange={e => setDesc(e.target.value)}
                  placeholder="Contract specification and domain responsibility..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: '#090d16',
                    border: '1px solid #334155',
                    borderRadius: 6,
                    color: '#fff',
                    boxSizing: 'border-box',
                    resize: 'vertical',
                  }}
                />
              </div>
              <button
                type="submit"
                style={{
                  padding: '10px 16px',
                  background: '#0284c7',
                  border: 'none',
                  borderRadius: 6,
                  color: '#fff',
                  fontWeight: 600,
                  cursor: 'pointer',
                  marginTop: 6,
                }}
              >
                Create Resource
              </button>
            </form>
          </div>
        </aside>
      </main>
    </div>
  )
}
