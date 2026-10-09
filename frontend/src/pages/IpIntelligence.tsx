import React, { useEffect, useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchIpList, fetchTopIpsFull } from '../services/api'
import {
  SectionTitle, LoadingState, RiskBadge, LabelBadge, MetricCard,
} from '../components/ui'

export default function IpIntelligencePage() {
  const nav = useNavigate()
  const [params] = useSearchParams()

  const [data, setData]     = useState<any>(null)
  const [topIps, setTopIps] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage]     = useState(1)
  const [search, setSearch] = useState(params.get('ip') || '')
  const [label, setLabel]   = useState('')
  const [sortBy, setSortBy] = useState('request_count')
  const [sortOrder, setSortOrder] = useState('desc')

  const PAGE_SIZE = 50

  const load = useCallback(() => {
    setLoading(true)
    fetchIpList({
      page, page_size: PAGE_SIZE,
      label: label || undefined,
      search: search || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    }).then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [page, search, label, sortBy, sortOrder])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    fetchTopIpsFull(5).then(setTopIps).catch(() => {})
  }, [])

  const rows = data?.data || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div>
      <SectionTitle
        title="IP Intelligence"
        sub="Per-IP activity analysis, risk scores, and behavioral indicators"
      />

      {/* Top IP quick cards */}
      {topIps.length > 0 && (
        <div className="metric-grid" style={{ marginBottom: 20 }}>
          {topIps.map((ip: any) => (
            <div
              key={ip.ip}
              className="metric-card"
              style={{ cursor: 'pointer' }}
              onClick={() => nav(`/ip-intelligence/${encodeURIComponent(ip.ip)}`)}
            >
              <div className="metric-label">{ip.ip}</div>
              <div className="metric-value metric-accent">
                {(ip.request_count || 0).toLocaleString()}
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {ip.dominant_label && <LabelBadge label={ip.dominant_label} />}
                {ip.risk_level && <RiskBadge level={ip.risk_level} />}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{
        display: 'flex', gap: 10, flexWrap: 'wrap',
        marginBottom: 16, alignItems: 'center',
      }}>
        <input
          className="input"
          placeholder="Search IP..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1) }}
          style={{ width: 200 }}
        />
        <select className="select" value={label}
                onChange={e => { setLabel(e.target.value); setPage(1) }}>
          <option value="">All Labels</option>
          <option value="scanner">Scanner</option>
          <option value="suspicious">Suspicious</option>
          <option value="bot">Bot</option>
          <option value="benign">Benign</option>
        </select>
        <select className="select" value={sortBy}
                onChange={e => { setSortBy(e.target.value); setPage(1) }}>
          <option value="request_count">Sort: Requests</option>
          <option value="risk_score">Sort: Risk Score</option>
          <option value="unique_ports">Sort: Unique Ports</option>
        </select>
        <select className="select" value={sortOrder}
                onChange={e => { setSortOrder(e.target.value); setPage(1) }}>
          <option value="desc">Desc</option>
          <option value="asc">Asc</option>
        </select>
        <div className="pagination-info">
          {total.toLocaleString()} IPs found
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>IP Address</th>
                  <th>Requests</th>
                  <th>Unique Ports</th>
                  <th>First Seen</th>
                  <th>Last Seen</th>
                  <th>Duration</th>
                  <th>Label</th>
                  <th>Risk</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row: any) => (
                  <tr
                    key={row.ip}
                    style={{ cursor: 'pointer' }}
                    onClick={() => nav(`/ip-intelligence/${encodeURIComponent(row.ip)}`)}
                  >
                    <td className="mono">{row.ip}</td>
                    <td style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)' }}>
                      {(row.request_count || 0).toLocaleString()}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {row.unique_ports ?? '—'}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '.72rem' }}>
                      {row.first_seen ? String(row.first_seen).slice(0, 16) : '—'}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '.72rem' }}>
                      {row.last_seen ? String(row.last_seen).slice(0, 16) : '—'}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '.72rem' }}>
                      {row.duration_seconds
                        ? `${Math.round(row.duration_seconds / 60)}m`
                        : '—'}
                    </td>
                    <td>
                      {row.dominant_label
                        ? <LabelBadge label={row.dominant_label} />
                        : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                    </td>
                    <td>{row.risk_level ? <RiskBadge level={row.risk_level} /> : '—'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                      {row.risk_score ?? '—'}
                    </td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={9} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
                      No IPs match the current filter
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '.75rem' }}
                    disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
              ← Prev
            </button>
            <span className="pagination-info">
              Page {page} / {totalPages}
            </span>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '.75rem' }}
                    disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  )
}
