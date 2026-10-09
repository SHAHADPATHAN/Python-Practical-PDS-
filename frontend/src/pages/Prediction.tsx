import React, { useState } from 'react'
import { postModelPredict } from '../services/api'
import { SectionTitle, MetricCard, LabelBadge, LoadingState } from '../components/ui'

const PRESETS = [
  {
    name: 'Gobuster Directory Fuzzer Attack',
    desc: 'High-frequency brute force scanning targeting admin endpoints',
    features: {
      bot_indicator_none: 1,
      scanner_indicator_none: 0,
      requests_per_ip_hour: 450,
      requests_per_ip_minute: 75,
      rapid_request: 1,
      rapid_request_5s: 1,
      rapid_request_1s: 1,
      rapid_and_high_volume: 1,
      scanner_and_high_volume: 1,
      user_agent_length: 16,
      user_agent_entropy: 2.8,
      is_browser: 0,
      unique_ports_per_ip: 1,
      unique_paths_per_ip: 412,
    },
  },
  {
    name: 'Legitimate Browser Session',
    desc: 'Standard human operator browsing pages via Chrome',
    features: {
      bot_indicator_none: 1,
      scanner_indicator_none: 1,
      requests_per_ip_hour: 12,
      requests_per_ip_minute: 2,
      rapid_request: 0,
      rapid_request_5s: 0,
      rapid_request_1s: 0,
      rapid_and_high_volume: 0,
      scanner_and_high_volume: 0,
      user_agent_length: 118,
      user_agent_entropy: 4.6,
      is_browser: 1,
      unique_ports_per_ip: 1,
      unique_paths_per_ip: 8,
    },
  },
  {
    name: 'Automated Scraping Bot',
    desc: 'Python-requests or crawler scraping content systematically',
    features: {
      bot_indicator_none: 0,
      scanner_indicator_none: 1,
      requests_per_ip_hour: 120,
      requests_per_ip_minute: 20,
      rapid_request: 1,
      rapid_request_5s: 1,
      rapid_request_1s: 0,
      rapid_and_high_volume: 0,
      scanner_and_high_volume: 0,
      user_agent_length: 24,
      user_agent_entropy: 3.2,
      is_browser: 0,
      unique_ports_per_ip: 1,
      unique_paths_per_ip: 95,
    },
  },
  {
    name: 'Suspicious Fuzzing / Probing',
    desc: 'Anomalous probes with high request rate and irregular paths',
    features: {
      bot_indicator_none: 1,
      scanner_indicator_none: 1,
      requests_per_ip_hour: 280,
      requests_per_ip_minute: 35,
      rapid_request: 1,
      rapid_request_5s: 1,
      rapid_request_1s: 1,
      rapid_and_high_volume: 1,
      scanner_and_high_volume: 0,
      user_agent_length: 45,
      user_agent_entropy: 3.9,
      is_browser: 0,
      unique_ports_per_ip: 4,
      unique_paths_per_ip: 180,
    },
  },
]

export default function PredictionPage() {
  const [features, setFeatures] = useState<Record<string, any>>({ ...PRESETS[0].features })
  const [result, setResult]     = useState<any | null>(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<string | null>(null)

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await postModelPredict(features)
      setResult(res)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setFeatures({ ...preset.features })
    setResult(null)
    setError(null)
  }

  const updateFeature = (key: string, val: any) => {
    setFeatures((prev) => ({ ...prev, [key]: val }))
  }

  return (
    <div>
      <SectionTitle
        title="Live Model Inference & Threat Classifier"
        sub="Test the trained Random Forest classifier against custom log vectors and synthetic attack scenarios"
      />

      {/* Preset Scenarios */}
      <div className="chart-container" style={{ marginBottom: 20 }}>
        <div className="chart-title">Load Preset Attack / Traffic Scenarios</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className="btn btn-secondary"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                padding: '12px 14px',
                textAlign: 'left',
                height: 'auto',
              }}
              onClick={() => applyPreset(p)}
            >
              <div style={{ fontWeight: 600, fontSize: '.85rem', color: 'var(--text-primary)' }}>
                {p.name}
              </div>
              <div style={{ fontSize: '.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
                {p.desc}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Features Input Form & Results */}
      <div className="grid-2">
        {/* Form */}
        <div className="chart-container">
          <div className="chart-title">Feature Vector Configuration</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Volume */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>requests_per_ip_hour</label>
                <input
                  type="number"
                  className="input"
                  value={features.requests_per_ip_hour || 0}
                  onChange={(e) => updateFeature('requests_per_ip_hour', Number(e.target.value))}
                />
              </div>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>requests_per_ip_minute</label>
                <input
                  type="number"
                  className="input"
                  value={features.requests_per_ip_minute || 0}
                  onChange={(e) => updateFeature('requests_per_ip_minute', Number(e.target.value))}
                />
              </div>
            </div>

            {/* Rapid requests */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.rapid_request)}
                  onChange={(e) => updateFeature('rapid_request', e.target.checked ? 1 : 0)}
                />
                rapid_request
              </label>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.rapid_request_5s)}
                  onChange={(e) => updateFeature('rapid_request_5s', e.target.checked ? 1 : 0)}
                />
                rapid_request_5s
              </label>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.rapid_request_1s)}
                  onChange={(e) => updateFeature('rapid_request_1s', e.target.checked ? 1 : 0)}
                />
                rapid_request_1s
              </label>
            </div>

            {/* User agent */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>user_agent_length</label>
                <input
                  type="number"
                  className="input"
                  value={features.user_agent_length || 0}
                  onChange={(e) => updateFeature('user_agent_length', Number(e.target.value))}
                />
              </div>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>user_agent_entropy (0 - 6.0)</label>
                <input
                  type="number"
                  step="0.1"
                  className="input"
                  value={features.user_agent_entropy || 0}
                  onChange={(e) => updateFeature('user_agent_entropy', Number(e.target.value))}
                />
              </div>
            </div>

            {/* Indicator flags */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.is_browser)}
                  onChange={(e) => updateFeature('is_browser', e.target.checked ? 1 : 0)}
                />
                is_browser (Chrome/Firefox)
              </label>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.scanner_and_high_volume)}
                  onChange={(e) => updateFeature('scanner_and_high_volume', e.target.checked ? 1 : 0)}
                />
                scanner_and_high_volume
              </label>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.bot_indicator_none)}
                  onChange={(e) => updateFeature('bot_indicator_none', e.target.checked ? 1 : 0)}
                />
                bot_indicator_none
              </label>
              <label style={{ fontSize: '.75rem', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={Boolean(features.scanner_indicator_none)}
                  onChange={(e) => updateFeature('scanner_indicator_none', e.target.checked ? 1 : 0)}
                />
                scanner_indicator_none
              </label>
            </div>

            {/* Ports and paths */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>unique_ports_per_ip</label>
                <input
                  type="number"
                  className="input"
                  value={features.unique_ports_per_ip || 1}
                  onChange={(e) => updateFeature('unique_ports_per_ip', Number(e.target.value))}
                />
              </div>
              <div>
                <label style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>unique_paths_per_ip</label>
                <input
                  type="number"
                  className="input"
                  value={features.unique_paths_per_ip || 1}
                  onChange={(e) => updateFeature('unique_paths_per_ip', Number(e.target.value))}
                />
              </div>
            </div>

            <button
              className="btn btn-primary"
              style={{ marginTop: 8, padding: '12px' }}
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Evaluating Model...' : 'Execute Classification Inference'}
            </button>
          </div>
        </div>

        {/* Prediction Output */}
        <div className="chart-container">
          <div className="chart-title">Inference Results</div>
          {loading ? (
            <LoadingState text="Computing Random Forest tree votes..." />
          ) : error ? (
            <div style={{ color: '#ef4444', padding: 20 }}>{error}</div>
          ) : result ? (
            <div>
              <div
                style={{
                  background: 'rgba(255,255,255,.03)',
                  padding: 20,
                  borderRadius: 8,
                  marginBottom: 20,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                  PREDICTED CLASSIFICATION
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 8 }}>
                  <LabelBadge label={result.prediction || 'benign'} />
                </div>
                <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>
                  Model Confidence:{' '}
                  <strong style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)' }}>
                    {result.confidence}%
                  </strong>
                </div>
              </div>

              {/* Probabilities */}
              {result.probabilities && (
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: '.8rem', fontWeight: 600, marginBottom: 10 }}>
                    Class Probabilities (200 Trees Voting)
                  </div>
                  {Object.entries(result.probabilities).map(([cls, prob]: [string, any]) => {
                    const pct = Math.round(Number(prob) * 100)
                    return (
                      <div key={cls} style={{ marginBottom: 8 }}>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            fontSize: '.75rem',
                            marginBottom: 4,
                          }}
                        >
                          <span style={{ textTransform: 'capitalize' }}>{cls}</span>
                          <span className="mono">{pct}%</span>
                        </div>
                        <div className="progress-bar-wrap" style={{ height: 8, background: 'rgba(255,255,255,0.06)' }}>
                          <div
                            className="progress-bar-fill"
                            style={{
                              width: `${pct}%`,
                              borderRadius: 4,
                              background:
                                cls === 'scanner'
                                  ? 'linear-gradient(90deg, #FF5722 0%, #FF8A34 100%)'
                                  : cls === 'suspicious'
                                  ? 'linear-gradient(90deg, #F59E0B 0%, #FBBF24 100%)'
                                  : cls === 'bot'
                                  ? 'linear-gradient(90deg, #8B5CF6 0%, #C084FC 100%)'
                                  : 'linear-gradient(90deg, #10B981 0%, #34D399 100%)',
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Top Signals */}
              {result.top_signals && (
                <div>
                  <div style={{ fontSize: '.8rem', fontWeight: 600, marginBottom: 8 }}>
                    Primary Model Weights
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {Object.entries(result.top_signals).map(([sig, val]: [string, any]) => (
                      <div
                        key={sig}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '.75rem',
                          padding: '4px 8px',
                          background: '#0a0a0a',
                          borderRadius: 4,
                        }}
                      >
                        <span className="mono" style={{ color: 'var(--text-muted)' }}>
                          {sig}
                        </span>
                        <span className="mono" style={{ color: 'var(--accent)' }}>
                          {(Number(val) * 100).toFixed(2)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a preset or adjust features and click "Execute Classification Inference"
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
