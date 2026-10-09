import React from 'react'

interface MetricCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'default' | 'orange' | 'green' | 'red' | 'yellow' | 'purple'
  icon?: React.ReactNode
}

const accentClass: Record<string, string> = {
  default: '',
  orange:  'metric-accent',
  green:   'metric-green',
  red:     'metric-red',
  yellow:  'metric-yellow',
  purple:  'metric-purple',
}

export function MetricCard({ label, value, sub, accent = 'default', icon }: MetricCardProps) {
  const cls = accentClass[accent] || ''
  const strVal = typeof value === 'number' ? value.toLocaleString() : String(value ?? '')

  let sizeClass = ''
  if (strVal.length > 15) {
    sizeClass = 'metric-value-xs'
  } else if (strVal.length > 10) {
    sizeClass = 'metric-value-sm'
  }

  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${cls} ${sizeClass}`} title={strVal}>
        {strVal}
      </div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  )
}

export function LoadingState({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="loading-state">
      <div className="spinner" />
      <span style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>{text}</span>
    </div>
  )
}

export function EmptyState({ title = 'No data', sub = '' }: { title?: string; sub?: string }) {
  return (
    <div className="empty-state">
      <div style={{ fontSize: '2rem' }}>📊</div>
      <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{title}</div>
      {sub && <div style={{ fontSize: '.78rem' }}>{sub}</div>}
    </div>
  )
}

export function RiskBadge({ level }: { level: string }) {
  const l = (level || 'LOW').toUpperCase()
  const cls = l === 'CRITICAL' ? 'badge-critical'
    : l === 'HIGH'     ? 'badge-high'
    : l === 'MEDIUM'   ? 'badge-medium'
    : 'badge-low'
  return <span className={`badge ${cls}`}>{l}</span>
}

export function LabelBadge({ label }: { label: string }) {
  const l = (label || '').toLowerCase()
  const cls = l === 'scanner'    ? 'badge-scanner'
    : l === 'suspicious' ? 'badge-suspicious'
    : l === 'bot'        ? 'badge-bot'
    : 'badge-benign'
  return <span className={`badge ${cls}`}>{label}</span>
}

export function SectionTitle({
  title, sub, actions,
}: { title: string; sub?: string; actions?: React.ReactNode }) {
  return (
    <div className="page-header">
      <div className="page-header-left">
        <h1>{title}</h1>
        {sub && <p>{sub}</p>}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  )
}

export function Alert({
  type = 'info', children,
}: { type?: 'info' | 'warning'; children: React.ReactNode }) {
  return (
    <div className={`alert alert-${type}`}>
      <span>{type === 'warning' ? '⚠️' : 'ℹ️'}</span>
      <span>{children}</span>
    </div>
  )
}

export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="progress-bar-wrap">
      <div className="progress-bar-fill" style={{ width: `${Math.min(100, value)}%` }} />
    </div>
  )
}
