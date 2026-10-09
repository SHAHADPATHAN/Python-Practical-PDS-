import React, { useEffect, useState, useCallback } from 'react'
import { fetchRecords, fetchRecordColumns } from '../services/api'
import { SectionTitle, LoadingState, LabelBadge } from '../components/ui'

export default function RecordsPage() {
  const [records, setRecords]       = useState<any[]>([])
  const [total, setTotal]           = useState(0)
  const [page, setPage]             = useState(1)
  const [pageSize, setPageSize]     = useState(50)
  const [label, setLabel]           = useState('')
  const [ipFilter, setIpFilter]     = useState('')
  const [search, setSearch]         = useState('')
  const [sortBy, setSortBy]         = useState('timestamp')
  const [sortOrder, setSortOrder]   = useState<'asc' | 'desc'>('asc')
  const [loading, setLoading]       = useState(true)
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null)
  const [columns, setColumns]       = useState<string[]>([])

  const loadData = useCallback(() => {
    setLoading(true)
    const params: Record<string, any> = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_order: sortOrder,
    }
    if (label) params.label = label
    if (ipFilter) params.ip = ipFilter
    if (search) params.search = search

    fetchRecords(params)
      .then((res) => {
        setRecords(res.records || [])
        setTotal(res.total || 0)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [page, pageSize, label, ipFilter, search, sortBy, sortOrder])

  useEffect(() => {
    fetchRecordColumns()
      .then((res) => {
        if (res?.columns) setColumns(res.columns)
      })
      .catch(console.error)
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadData()
  }

  const totalPages = Math.ceil(total / pageSize) || 1

  return (
    <div>
      <SectionTitle
        title="Log Records Explorer"
        sub={`Browsing balanced & processed log dataset (${total.toLocaleString()} matching records)`}
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                const jsonStr = JSON.stringify(records, null, 2)
                const blob = new Blob([jsonStr], { type: 'application/json' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `pds_records_page_${page}.json`
                a.click()
              }}
            >
              Export Page (JSON)
            </button>
          </div>
        }
      />

      {/* Filter and search bar */}
      <div className="filter-bar" style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', marginBottom: 16 }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: 10, flex: 1, minWidth: 300 }}>
          <input
            type="text"
            className="input"
            placeholder="Search path, user agent, or query..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1 }}
          />
          <input
            type="text"
            className="input"
            placeholder="Filter IP..."
            value={ipFilter}
            onChange={(e) => setIpFilter(e.target.value)}
            style={{ width: 160 }}
          />
          <button type="submit" className="btn btn-primary">
            Filter
          </button>
        </form>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <select
            className="select"
            value={label}
            onChange={(e) => {
              setLabel(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All Labels</option>
            <option value="scanner">Scanner</option>
            <option value="suspicious">Suspicious</option>
            <option value="bot">Bot</option>
            <option value="benign">Benign</option>
          </select>

          <select
            className="select"
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value))
              setPage(1)
            }}
          >
            <option value={25}>25 / page</option>
            <option value={50}>50 / page</option>
            <option value={100}>100 / page</option>
          </select>

          <button
            className="btn btn-ghost"
            onClick={() => {
              setLabel('')
              setIpFilter('')
              setSearch('')
              setPage(1)
            }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 40 }}>
            <LoadingState text="Loading log records..." />
          </div>
        ) : records.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            No records matched your filter criteria.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ width: 50 }}>#</th>
                  <th>Timestamp</th>
                  <th>IP Address</th>
                  <th>Method</th>
                  <th>Path</th>
                  <th>Status</th>
                  <th>Bytes</th>
                  <th>Label</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, idx) => (
                  <tr
                    key={r.id || idx}
                    onClick={() => setSelectedRecord(r)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ color: 'var(--text-muted)' }}>
                      {(page - 1) * pageSize + idx + 1}
                    </td>
                    <td className="mono" style={{ fontSize: '.75rem', whiteSpace: 'nowrap' }}>
                      {r.timestamp || r.time || '—'}
                    </td>
                    <td className="mono" style={{ color: 'var(--accent)' }}>
                      {r.ip || r.client_ip || '—'}
                    </td>
                    <td>
                      <span className="badge" style={{ background: '#27272a' }}>
                        {r.method || r.http_method || 'GET'}
                      </span>
                    </td>
                    <td
                      style={{
                        maxWidth: 240,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '.75rem',
                      }}
                      title={r.path || r.url}
                    >
                      {r.path || r.url || '/'}
                    </td>
                    <td>
                      <span
                        className="mono"
                        style={{
                          color:
                            String(r.response_code || r.status).startsWith('2')
                              ? '#22c55e'
                              : String(r.response_code || r.status).startsWith('4')
                              ? '#eab308'
                              : '#ef4444',
                        }}
                      >
                        {r.response_code || r.status || '200'}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '.75rem' }}>
                      {(r.packet_size || r.bytes || 0).toLocaleString()}
                    </td>
                    <td>
                      <LabelBadge label={r.label || 'benign'} />
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost"
                        style={{ padding: '2px 8px', fontSize: '.7rem' }}
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedRecord(r)
                        }}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination footer */}
        <div
          style={{
            padding: '12px 20px',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '.75rem',
            color: 'var(--text-muted)',
          }}
        >
          <div>
            Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, total)} of {total.toLocaleString()} records
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <button
              className="btn btn-ghost"
              disabled={page <= 1}
              onClick={() => setPage(1)}
              style={{ padding: '4px 8px' }}
            >
              «
            </button>
            <button
              className="btn btn-ghost"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              style={{ padding: '4px 8px' }}
            >
              Prev
            </button>
            <span style={{ color: 'var(--text-primary)', padding: '0 8px' }}>
              Page {page} of {totalPages}
            </span>
            <button
              className="btn btn-ghost"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              style={{ padding: '4px 8px' }}
            >
              Next
            </button>
            <button
              className="btn btn-ghost"
              disabled={page >= totalPages}
              onClick={() => setPage(totalPages)}
              style={{ padding: '4px 8px' }}
            >
              »
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal / Drawer */}
      {selectedRecord && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 20,
          }}
          onClick={() => setSelectedRecord(null)}
        >
          <div
            style={{
              backgroundColor: '#161616',
              border: '1px solid var(--border-strong)',
              borderRadius: 8,
              width: '100%',
              maxWidth: 700,
              maxHeight: '85vh',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Log Record Details</h3>
                <LabelBadge label={selectedRecord.label || 'benign'} />
              </div>
              <button
                className="btn btn-ghost"
                onClick={() => setSelectedRecord(null)}
                style={{ fontSize: '1.2rem', padding: '0 6px', lineHeight: 1 }}
              >
                ×
              </button>
            </div>
            <div style={{ padding: 20, overflowY: 'auto' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>IP ADDRESS</div>
                  <div className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                    {selectedRecord.ip || selectedRecord.client_ip || '—'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>TIMESTAMP</div>
                  <div className="mono" style={{ fontSize: '.8rem' }}>
                    {selectedRecord.timestamp || selectedRecord.time || '—'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>METHOD & STATUS</div>
                  <div className="mono">
                    {selectedRecord.method || 'GET'} — {selectedRecord.response_code || selectedRecord.status || '200'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>PACKET SIZE</div>
                  <div className="mono">
                    {(selectedRecord.packet_size || selectedRecord.bytes || 0).toLocaleString()} bytes
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>REQUEST URL / PATH</div>
                <div
                  className="mono"
                  style={{
                    padding: 8,
                    background: '#0a0a0a',
                    borderRadius: 4,
                    fontSize: '.75rem',
                    wordBreak: 'break-all',
                  }}
                >
                  {selectedRecord.path || selectedRecord.url || '/'}
                </div>
              </div>

              {selectedRecord.user_agent && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>USER AGENT</div>
                  <div
                    className="mono"
                    style={{
                      padding: 8,
                      background: '#0a0a0a',
                      borderRadius: 4,
                      fontSize: '.75rem',
                      wordBreak: 'break-all',
                    }}
                  >
                    {selectedRecord.user_agent}
                  </div>
                </div>
              )}

              <div>
                <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>COMPLETE RECORD JSON</div>
                <pre
                  style={{
                    padding: 12,
                    background: '#0a0a0a',
                    borderRadius: 4,
                    fontSize: '.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: '#a1a1aa',
                    maxHeight: 220,
                    overflowY: 'auto',
                  }}
                >
                  {JSON.stringify(selectedRecord, null, 2)}
                </pre>
              </div>
            </div>
            <div
              style={{
                padding: '12px 20px',
                borderTop: '1px solid var(--border)',
                display: 'flex',
                justifyContent: 'flex-end',
              }}
            >
              <button className="btn btn-secondary" onClick={() => setSelectedRecord(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
