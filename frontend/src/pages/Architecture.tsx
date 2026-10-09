import React from 'react'
import { SectionTitle, MetricCard } from '../components/ui'

const PIPELINE_STAGES = [
  { step: '01', title: 'Raw Ingestion', tool: 'Load & Explore', file: 'cj.log (215 MB)', desc: 'Reads 2.06M raw lines with streaming chunk readers.' },
  { step: '02', title: 'Syntactic Parsing', tool: 'Parse & Structure', file: 'structured_logs.csv', desc: 'Recovers JSON arrays and fixes malformed quote delimiters.' },
  { step: '03', title: 'Data Cleaning', tool: 'Clean & Preprocess', file: 'cleaned_logs.csv', desc: 'Standardizes UTC dates, validates IPv4, and parses HTTP verbs.' },
  { step: '04', title: 'Threat Labeling', tool: 'Attack Labeling', file: 'labeled_logs.csv', desc: 'Identifies Gobuster, DirBuster, Nmap, bots, and benign traffic.' },
  { step: '05', title: 'Feature Engineering', tool: 'Feature Engineering', file: 'features.csv (746 MB)', desc: 'Computes 33 behavioral, entropy, and temporal signals.' },
  { step: '06', title: 'Stratified Balancing', tool: 'Data Balancing', file: 'balanced_logs.csv (18k)', desc: 'Equalizes classes at 4,576 records to prevent majority bias.' },
  { step: '07', title: 'Data Wrangling', tool: 'Data Wrangling', file: 'ip_summary & pivots', desc: 'Constructs IP profiles and 24-hr time-series cross-tabulations.' },
  { step: '08', title: 'Visual EDA', tool: 'EDA & Visualisation', file: '8 High-Res Figures', desc: 'Analyzes peak diurnal bursts, IP concentration, and tool signatures.' },
  { step: '09', title: 'Supervised ML', tool: 'Machine Learning', file: 'random_forest (99.2%)', desc: 'Trains 200-tree ensemble with leakage analysis.' },
  { step: '10', title: 'Reusable Pipeline', tool: 'End-to-End Pipeline', file: 'pipeline_features.csv', desc: 'Modular class-based engine for streaming log intelligence.' },
]

export default function ArchitecturePage() {
  return (
    <div>
      <SectionTitle
        title="System Architecture & Data Science Pipeline"
        sub="End-to-end blueprint detailing log parsing, feature extraction, ML classification, and full-stack API integration"
      />

      {/* Metrics */}
      <div className="metric-grid">
        <MetricCard label="Pipeline Practicals" value="10 / 10" sub="All practicals connected" accent="green" />
        <MetricCard label="Backend Engine" value="FastAPI" sub="Python Asynchronous REST" accent="orange" />
        <MetricCard label="Frontend Framework" value="React 19" sub="TypeScript + Vite SPA" accent="purple" />
        <MetricCard label="Classifiers Loaded" value="Random Forest" sub="200 estimators (99.21% F1)" accent="yellow" />
      </div>

      {/* Pipeline Stages Flow */}
      <div className="chart-container" style={{ marginBottom: 24 }}>
        <div className="chart-title">The 10-Stage Data Science Execution Pipeline</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14, marginTop: 16 }}>
          {PIPELINE_STAGES.map((s) => (
            <div
              key={s.step}
              style={{
                background: 'rgba(255,255,255,.02)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '14px 16px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span className="mono" style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '.9rem' }}>
                  STAGE {s.step}
                </span>
                <span className="badge" style={{ fontSize: '.65rem' }}>{s.tool}</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: '.85rem', color: 'var(--text-primary)', marginBottom: 4 }}>
                {s.title}
              </div>
              <div className="mono" style={{ fontSize: '.7rem', color: '#a1a1aa', marginBottom: 6 }}>
                Artifact: {s.file}
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
                {s.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full-Stack Layers */}
      <div className="grid-2">
        <div className="chart-container">
          <div className="chart-title">Backend Architecture (Python / FastAPI)</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                Modular Log Parsers
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Specialized parsers for CJ Log arrays, Apache Combined/Common, Nginx access logs, JSON objects, and CSV tables with regex tokenizers.
              </div>
            </div>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                In-Memory Cache & Smart Data Slicing
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                High-performance cache layer preventing redundant loading of the 746 MB features dataset while serving sub-millisecond API responses.
              </div>
            </div>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                Joblib ML Model Runtime
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Deserializes <code>random_forest_classifier.joblib</code> with label encoder to execute live inference against synthetic or incoming vectors.
              </div>
            </div>
          </div>
        </div>

        <div className="chart-container">
          <div className="chart-title">Frontend Architecture (React / TypeScript / Vite)</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                SOC / SIEM Dark Cyber Theme
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Tailored with <code>#0A0A0A</code> deep black background, vivid <code>#F97316</code> security orange accents, and JetBrains Mono code typography.
              </div>
            </div>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                Dynamic Interactive Visualizations
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Recharts responsive donut charts, horizontal bar hierarchies, 24-hr temporal heatmaps, and publication figure viewers.
              </div>
            </div>
            <div style={{ padding: 12, background: '#0a0a0a', borderRadius: 6, border: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '.85rem' }}>
                Live Stream Playground & Drag-Drop Ingestion
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Direct file streaming with real-time feedback, sample attacks testbench, and instantaneous feature vector prediction.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
