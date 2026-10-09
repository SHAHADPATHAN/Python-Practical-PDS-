import React, { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { SectionTitle, Alert, MetricCard } from '../components/ui'

const SCANNER_DETAILS: Record<string, { desc: string; category: string }> = {
  gobuster: {
    desc: 'Web content/directory scanner using wordlists (written in Go)',
    category: 'Directory Fuzzer',
  },
  dirbuster: {
    desc: 'Multi-threaded Java application for web directory/file brute-forcing',
    category: 'Directory Fuzzer',
  },
  nmap: {
    desc: 'Network mapping and port scanning tool (Nmap Scripting Engine)',
    category: 'Network Scanner',
  },
  nikto: {
    desc: 'Comprehensive web server vulnerability scanner',
    category: 'Vulnerability Scanner',
  },
  zgrab: {
    desc: 'Fast application-layer scanner (Zmap banner grabbing project)',
    category: 'Banner Grabber',
  },
  nessus: {
    desc: 'Enterprise vulnerability assessment tool by Tenable',
    category: 'Vulnerability Assessment',
  },
  masscan: {
    desc: 'Extremely fast internet-wide asynchronous port scanner',
    category: 'Port Scanner',
  },
  wpscan: {
    desc: 'Black box WordPress vulnerability and plugin scanner',
    category: 'CMS Scanner',
  },
}

const BOT_DETAILS: Record<string, { desc: string; category: string }> = {
  'python-requests': { desc: 'Python HTTP client library — common in custom automated scripts', category: 'Scripting Client' },
  'go-http-client':  { desc: 'Go standard net/http client — automated microservices / crawlers', category: 'Automated Client' },
  bot:               { desc: 'Generic bot identifier in user-agent string', category: 'General Bot' },
  spider:            { desc: 'Web spider indexing and link extraction engine', category: 'Crawler / Spider' },
  'curl/':           { desc: 'Command-line curl utility for automated querying', category: 'CLI Client' },
  crawler:           { desc: 'Systematic web content crawler', category: 'Crawler' },
}

const SCANNER_COUNTS: Record<string, number> = {
  gobuster: 1_408_510, dirbuster: 397_212, nmap: 9_204,
  nikto: 7_044, zgrab: 4_219, nessus: 718, masscan: 437, wpscan: 23,
}

const BOT_COUNTS: Record<string, number> = {
  'python-requests': 2_276, 'go-http-client': 2_166,
  bot: 106, spider: 15, 'curl/': 8, crawler: 5,
}

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
      <p style={{ color: '#94A3B8', marginBottom: 4, fontWeight: 700, textTransform: 'uppercase' }}>
        {label}
      </p>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 14 }}>
          <span style={{ color: p.color || '#CBD5E1' }}>{p.name}:</span>
          <span style={{ color: '#F8FAFC', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
            {(p.value || 0).toLocaleString()} records
          </span>
        </div>
      ))}
    </div>
  )
}

export default function SecurityPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const total = 2_060_520

  const scannerRows = Object.entries(SCANNER_COUNTS).map(([tool, records]) => ({
    tool,
    records,
    pct: ((records / total) * 100).toFixed(4),
    ...SCANNER_DETAILS[tool],
  }))

  const botRows = Object.entries(BOT_COUNTS).map(([tool, records]) => ({
    tool,
    records,
    pct: ((records / total) * 100).toFixed(4),
    ...BOT_DETAILS[tool],
  }))

  const detail = selected
    ? (scannerRows.find(r => r.tool === selected) || botRows.find(r => r.tool === selected))
    : null

  const chartData = [...scannerRows].slice(0, 8)

  return (
    <div>
      <SectionTitle
        title="Threat Actors & Tool Intelligence"
        sub="In-depth signature analysis of automated scanning frameworks and automated bot clients"
      />

      <Alert type="warning">
        <strong>Security Classification Taxonomy:</strong> "Scanner" identifies a verifiable security tool signature in the user-agent header.
        This provides threat reconnaissance telemetry and does not necessarily imply unauthorized hostile intent, as authorized auditors and white-hat researchers use these tools.
      </Alert>

      {/* Top metrics */}
      <div className="metric-grid">
        <MetricCard label="Scanner Volume" value={1_827_367} sub="88.68% of dataset" accent="orange" />
        <MetricCard label="Bot Volume" value={4_576} sub="0.22% of dataset" accent="purple" />
        <MetricCard label="Gobuster Traffic" value={1_408_510} sub="68.36% of all logs" accent="orange" />
        <MetricCard label="DirBuster Traffic" value={397_212} sub="19.28% of all logs" accent="orange" />
      </div>

      {/* Charts Section */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Scanner Breakdown */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Scanner Signatures (Click to Inspect)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--accent)' }}>8 TOOLS IDENTIFIED</span>
          </div>
          <ResponsiveContainer width="100%" height={290}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 20, bottom: 5, left: 75 }}
              onClick={(e: any) => e?.activePayload && setSelected(e.activePayload[0]?.payload?.tool)}
            >
              <defs>
                <linearGradient id="secScannerGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#FF5722" />
                  <stop offset="100%" stopColor="#FFA04D" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }}
                     tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : String(v)}
                     tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis type="category" dataKey="tool"
                     tick={{ fill: '#CBD5E1', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                     tickLine={false} axisLine={false} />
              <Tooltip content={<GlassTooltip />} />
              <Bar dataKey="records" name="Records" radius={[0, 6, 6, 0]}>
                {chartData.map(entry => (
                  <Cell
                    key={entry.tool}
                    fill={entry.tool === selected ? '#FF8A34' : 'url(#secScannerGrad)'}
                    opacity={selected && entry.tool !== selected ? 0.45 : 1}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Bot Clients Breakdown */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Automated Bot & Scripting Clients</span>
            <span style={{ fontSize: '.68rem', color: 'var(--label-bot)' }}>4,576 SAMPLES</span>
          </div>
          <ResponsiveContainer width="100%" height={290}>
            <BarChart
              data={botRows}
              layout="vertical"
              margin={{ top: 5, right: 20, bottom: 5, left: 110 }}
              onClick={(e: any) => e?.activePayload && setSelected(e.activePayload[0]?.payload?.tool)}
            >
              <defs>
                <linearGradient id="secBotGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#8B5CF6" />
                  <stop offset="100%" stopColor="#C084FC" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }}
                     tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis type="category" dataKey="tool"
                     tick={{ fill: '#CBD5E1', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                     tickLine={false} axisLine={false} />
              <Tooltip content={<GlassTooltip />} />
              <Bar dataKey="records" name="Records" radius={[0, 6, 6, 0]}>
                {botRows.map(entry => (
                  <Cell
                    key={entry.tool}
                    fill={entry.tool === selected ? '#A855F7' : 'url(#secBotGrad)'}
                    opacity={selected && entry.tool !== selected ? 0.45 : 1}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Selected Tool Detail Drawer / Card */}
      {detail && (
        <div className="chart-container" style={{ marginBottom: 24, border: '1px solid rgba(255, 107, 0, 0.4)', background: 'rgba(255, 107, 0, 0.04)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="mono" style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent)' }}>
                {detail.tool.toUpperCase()}
              </span>
              <span className="badge" style={{ background: 'rgba(255, 107, 0, 0.15)', color: 'var(--accent)' }}>
                {(detail as any).category}
              </span>
            </div>
            <button className="btn btn-ghost" style={{ fontSize: '.75rem' }} onClick={() => setSelected(null)}>
              ✕ Dismiss
            </button>
          </div>
          <div className="grid-3" style={{ gap: 16 }}>
            <div>
              <div style={{ fontSize: '.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Volume Count</div>
              <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#F8FAFC' }}>
                {detail.records.toLocaleString()}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Share of Complete Logs</div>
              <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent)' }}>
                {detail.pct}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tool Characteristic</div>
              <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {(detail as any).desc}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Tables */}
      <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div className="chart-title" style={{ margin: 0 }}>Full Security Signature Inventory</div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Signature Tool</th>
                <th>Category</th>
                <th>Observed Records</th>
                <th>Dataset Share</th>
                <th>Signature Profile</th>
              </tr>
            </thead>
            <tbody>
              {scannerRows.map(row => (
                <tr key={row.tool} style={{ cursor: 'pointer' }} onClick={() => setSelected(row.tool === selected ? null : row.tool)}>
                  <td className="mono" style={{ color: 'var(--accent)', fontWeight: 700 }}>{row.tool}</td>
                  <td><span className="badge" style={{ background: 'rgba(255,255,255,0.05)' }}>{row.category}</span></td>
                  <td className="mono" style={{ color: '#F8FAFC', fontWeight: 600 }}>{row.records.toLocaleString()}</td>
                  <td className="mono">{row.pct}%</td>
                  <td style={{ fontSize: '.76rem' }}>{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
