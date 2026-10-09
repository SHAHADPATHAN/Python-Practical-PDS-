import React from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { SectionTitle, MetricCard, LabelBadge, Alert } from '../components/ui'

const IMBALANCED_DATA = [
  { label: 'Scanner', count: 1_827_367, percentage: 88.68, fill: '#FF5722' },
  { label: 'Suspicious', count: 167_486, percentage: 8.13, fill: '#F59E0B' },
  { label: 'Benign', count: 61_091, percentage: 2.96, fill: '#10B981' },
  { label: 'Bot', count: 4_576, percentage: 0.22, fill: '#8B5CF6' },
]

const BALANCED_DATA = [
  { label: 'Scanner', count: 4_576, percentage: 25.0, fill: '#FF5722' },
  { label: 'Suspicious', count: 4_576, percentage: 25.0, fill: '#F59E0B' },
  { label: 'Benign', count: 4_576, percentage: 25.0, fill: '#10B981' },
  { label: 'Bot', count: 4_576, percentage: 25.0, fill: '#8B5CF6' },
]

const GlassTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'rgba(13, 19, 34, 0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      boxShadow: '0 12px 30px rgba(0,0,0,0.6)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: '.75rem',
    }}>
      <p style={{ color: '#94A3B8', marginBottom: 4, fontWeight: 700, textTransform: 'capitalize' }}>
        {label} Class
      </p>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 14 }}>
          <span style={{ color: p.color || '#CBD5E1' }}>Samples:</span>
          <span style={{ color: '#F8FAFC', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
            {(p.value || 0).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function BalancingPage() {
  return (
    <div>
      <SectionTitle
        title="Class Imbalance & Stratified Balancing"
        sub="Practical 06: Mitigation of 400:1 raw class skew through controlled random undersampling"
      />

      {/* Metric Cards */}
      <div className="metric-grid">
        <MetricCard
          label="Raw Skew Ratio"
          value="400 : 1"
          sub="Scanner (1.8M) vs Bot (4.5k)"
          accent="red"
        />
        <MetricCard
          label="Balanced Cohort"
          value="18,304"
          sub="4,576 records × 4 classes"
          accent="green"
        />
        <MetricCard
          label="Anchor Minority"
          value="Bot (4,576)"
          sub="Determined undersample target"
          accent="purple"
        />
        <MetricCard
          label="Balancing Strategy"
          value="Stratified Undersampling"
          sub="Zero synthetic interpolation"
          accent="orange"
        />
      </div>

      <div style={{ marginBottom: 20 }}>
        <Alert type="info">
          <strong>Methodology Rationale:</strong> The raw access log is overwhelmingly dominated by automated directory
          fuzzers (Gobuster / DirBuster) making up 88.68% of events. Without balancing, a naive ML classifier predicting
          only <em>Scanner</em> would achieve 88.7% accuracy with 0% bot/benign detection. Practical 06 balances all four
          classes equally at 4,576 samples per class to train un-skewed decision boundaries.
        </Alert>
      </div>

      {/* Comparison Charts */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Imbalanced Chart */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Before Balancing: Raw Dataset (2,060,520 records)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--risk-critical)' }}>88.7% DOMINANT</span>
          </div>
          <ResponsiveContainer width="100%" height={270}>
            <BarChart data={IMBALANCED_DATA} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,.04)" vertical={false} />
              <XAxis dataKey="label" tick={{ fill: '#64748B', fontSize: 11 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis
                tick={{ fill: '#64748B', fontSize: 10 }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<GlassTooltip />} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {IMBALANCED_DATA.map((entry) => (
                  <Cell key={entry.label} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: '.74rem', color: 'var(--text-muted)', marginTop: 10, textAlign: 'center' }}>
            Extreme skew: Scanners represent 88.68% while Bots are only 0.22%
          </div>
        </div>

        {/* Balanced Chart */}
        <div className="chart-container">
          <div className="chart-title">
            <span>After Balancing: Equalized Matrix (18,304 records)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--risk-low)' }}>PERFECT 25% PARITY</span>
          </div>
          <ResponsiveContainer width="100%" height={270}>
            <BarChart data={BALANCED_DATA} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,.04)" vertical={false} />
              <XAxis dataKey="label" tick={{ fill: '#64748B', fontSize: 11 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip content={<GlassTooltip />} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {BALANCED_DATA.map((entry) => (
                  <Cell key={entry.label} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: '.74rem', color: 'var(--text-muted)', marginTop: 10, textAlign: 'center' }}>
            Balanced 25.0% split across all 4 target classes (4,576 records each)
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div className="chart-title" style={{ margin: 0 }}>Class Distribution Comparison Matrix</div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Class Label</th>
                <th>Raw Count</th>
                <th>Raw Proportion</th>
                <th>Balanced Count</th>
                <th>Balanced Proportion</th>
                <th>Undersampling Factor</th>
              </tr>
            </thead>
            <tbody>
              {IMBALANCED_DATA.map((item, idx) => {
                const b = BALANCED_DATA[idx]
                const factor = (item.count / b.count).toFixed(1)
                return (
                  <tr key={item.label}>
                    <td>
                      <LabelBadge label={item.label} />
                    </td>
                    <td className="mono" style={{ color: 'var(--text-primary)' }}>
                      {item.count.toLocaleString()}
                    </td>
                    <td className="mono">{item.percentage}%</td>
                    <td className="mono" style={{ color: 'var(--accent)', fontWeight: 700 }}>
                      {b.count.toLocaleString()}
                    </td>
                    <td className="mono" style={{ color: '#10B981', fontWeight: 600 }}>25.0%</td>
                    <td className="mono" style={{ color: Number(factor) > 1 ? '#FF6B00' : '#10B981' }}>
                      {factor}x downsampled
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
