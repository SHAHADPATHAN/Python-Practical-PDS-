import React, { useEffect, useState } from 'react'
import { fetchPracticals, fetchPractical } from '../services/api'
import { SectionTitle, LoadingState } from '../components/ui'

export default function PracticalsPage() {
  const [practicals, setPracticals] = useState<any[]>([])
  const [selected, setSelected]     = useState<any | null>(null)
  const [activeTab, setActiveTab]   = useState<'solution' | 'code' | 'report'>('solution')
  const [detailLoading, setDetailLoading] = useState(false)
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    fetchPracticals()
      .then((res) => {
        setPracticals(res || [])
        setLoading(false)
        if (res && res.length > 0) {
          loadDetail(res[0].id)
        }
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const loadDetail = (id: number) => {
    setDetailLoading(true)
    fetchPractical(id)
      .then((res) => {
        setSelected(res)
        setDetailLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setDetailLoading(false)
      })
  }

  if (loading) return <LoadingState text="Loading practicals curriculum & solutions..." />

  return (
    <div>
      <SectionTitle
        title="University Data Science Practicals (01 – 10)"
        sub="Complete curriculum solutions: theoretical formulations, Python implementation scripts, execution reports, and viva examination preparation"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 24, alignItems: 'flex-start' }}>
        {/* Left Practicals List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {practicals.map((p) => {
            const isSelected = selected?.id === p.id
            return (
              <div
                key={p.id}
                onClick={() => loadDetail(p.id)}
                style={{
                  backgroundColor: isSelected ? 'rgba(255, 107, 0, 0.08)' : 'var(--bg-card)',
                  border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 10,
                  padding: '14px 16px',
                  cursor: 'pointer',
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                  boxShadow: isSelected ? '0 0 16px rgba(255, 107, 0, 0.15)' : 'none',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span
                    className="mono"
                    style={{
                      fontSize: '.74rem',
                      color: isSelected ? 'var(--accent)' : 'var(--text-muted)',
                      fontWeight: 700,
                    }}
                  >
                    PRACTICAL {String(p.id).padStart(2, '0')}
                  </span>
                  <span
                    className="badge"
                    style={{
                      backgroundColor: 'rgba(16, 185, 129, 0.15)',
                      color: '#34D399',
                      fontSize: '.62rem',
                    }}
                  >
                    COMPLETED
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '.88rem', color: isSelected ? '#F8FAFC' : 'var(--text-primary)' }}>
                  {p.title}
                </div>
                <div style={{ fontSize: '.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                  {p.key_result}
                </div>
              </div>
            )
          })}
        </div>

        {/* Right Detail Pane */}
        <div className="chart-container" style={{ minHeight: 650 }}>
          {detailLoading ? (
            <LoadingState text="Loading comprehensive practical solution..." />
          ) : selected ? (
            <div>
              {/* Header Title */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div>
                  <div className="mono" style={{ color: 'var(--accent)', fontSize: '.78rem', fontWeight: 700, letterSpacing: '.06em' }}>
                    PRACTICAL {String(selected.id).padStart(2, '0')} SOLUTION GUIDE
                  </div>
                  <h2 style={{ fontSize: '1.45rem', fontWeight: 800, margin: '4px 0 6px', letterSpacing: '-0.02em' }}>
                    {selected.title}
                  </h2>
                  <p style={{ fontSize: '.84rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {selected.objective}
                  </p>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div style={{
                display: 'flex',
                gap: 6,
                borderBottom: '1px solid var(--border)',
                marginBottom: 20,
                paddingBottom: 2,
              }}>
                {[
                  { key: 'solution', label: 'Solution Guide & Methodology', icon: '📋' },
                  { key: 'code',     label: `Python Script (${selected.script})`, icon: '🐍' },
                  { key: 'report',   label: 'Execution Report Output', icon: '📄' },
                ].map(t => (
                  <button
                    key={t.key}
                    type="button"
                    className="btn"
                    style={{
                      background: activeTab === t.key ? 'var(--accent-dim)' : 'transparent',
                      color: activeTab === t.key ? 'var(--accent)' : 'var(--text-muted)',
                      border: `1px solid ${activeTab === t.key ? 'rgba(255, 107, 0, 0.35)' : 'transparent'}`,
                      borderRadius: 6,
                      fontSize: '.75rem',
                      padding: '8px 14px',
                    }}
                    onClick={() => setActiveTab(t.key as any)}
                  >
                    <span>{t.icon}</span>
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>

              {/* Tab 1: Solution Guide */}
              {activeTab === 'solution' && (
                <div>
                  {/* Aim */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 4 }}>
                      Problem Statement & Aim
                    </div>
                    <div style={{
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      padding: 14,
                      fontSize: '.82rem',
                      color: '#F8FAFC',
                      lineHeight: 1.5,
                    }}>
                      {selected.aim || selected.objective}
                    </div>
                  </div>

                  {/* Theoretical Concept */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--cyan)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 4 }}>
                      Theoretical Foundations & Concepts
                    </div>
                    <div style={{
                      background: 'rgba(6, 182, 212, 0.04)',
                      border: '1px solid rgba(6, 182, 212, 0.2)',
                      borderRadius: 8,
                      padding: 14,
                      fontSize: '.82rem',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.6,
                    }}>
                      {selected.theory || 'Standard data science and distributed server log preprocessing.'}
                    </div>
                  </div>

                  {/* Step-by-Step Methodology */}
                  {selected.steps && (
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ fontSize: '.72rem', fontWeight: 700, color: '#34D399', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>
                        Step-by-Step Implementation Flow
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selected.steps.map((st: string, idx: number) => (
                          <div
                            key={idx}
                            style={{
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: 12,
                              background: 'rgba(255,255,255,0.02)',
                              border: '1px solid var(--border)',
                              borderRadius: 6,
                              padding: '10px 14px',
                            }}
                          >
                            <span className="mono" style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '.8rem', minWidth: 24 }}>
                              {String(idx + 1).padStart(2, '0')}.
                            </span>
                            <span style={{ fontSize: '.8rem', color: '#E2E8F0', lineHeight: 1.4 }}>
                              {st}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Specs & Artifacts Table */}
                  <div style={{ marginTop: 24 }}>
                    <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>
                      Technical Specifications & Artifacts
                    </div>
                    <table className="data-table" style={{ width: '100%' }}>
                      <tbody>
                        <tr>
                          <td style={{ color: 'var(--text-muted)', width: 160 }}>Source Script</td>
                          <td className="mono" style={{ color: 'var(--accent)' }}>practicals/{selected.script}</td>
                        </tr>
                        <tr>
                          <td style={{ color: 'var(--text-muted)' }}>Input Dataset</td>
                          <td className="mono">{selected.input}</td>
                        </tr>
                        <tr>
                          <td style={{ color: 'var(--text-muted)' }}>Generated Artifact</td>
                          <td className="mono" style={{ color: '#06B6D4' }}>{selected.output}</td>
                        </tr>
                        <tr>
                          <td style={{ color: 'var(--text-muted)' }}>Verified Outcome</td>
                          <td style={{ color: '#34D399', fontWeight: 600 }}>{selected.key_result}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 2: Python Source Code */}
              {activeTab === 'code' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <div className="mono" style={{ fontSize: '.78rem', color: 'var(--text-muted)' }}>
                      Location: <strong style={{ color: 'var(--accent)' }}>practicals/{selected.script}</strong>
                    </div>
                    {selected.script_content && (
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '.72rem', padding: '4px 10px' }}
                          onClick={() => {
                            navigator.clipboard.writeText(selected.script_content)
                            alert('Source code copied to clipboard!')
                          }}
                        >
                          Copy Script
                        </button>
                        <button
                          className="btn btn-primary"
                          style={{ fontSize: '.72rem', padding: '4px 10px' }}
                          onClick={() => {
                            const blob = new Blob([selected.script_content], { type: 'text/plain' })
                            const url = URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = selected.script
                            a.click()
                          }}
                        >
                          Download .py
                        </button>
                      </div>
                    )}
                  </div>

                  {selected.script_content ? (
                    <pre
                      style={{
                        background: '#060911',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        padding: 18,
                        fontSize: '.74rem',
                        fontFamily: 'var(--font-mono)',
                        color: '#E2E8F0',
                        maxHeight: 520,
                        overflowY: 'auto',
                        whiteSpace: 'pre',
                        lineHeight: 1.55,
                      }}
                    >
                      {selected.script_content}
                    </pre>
                  ) : (
                    <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
                      Source script file could not be read.
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Execution Report Output */}
              {activeTab === 'report' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
                      Report Artifact: <strong className="mono">{selected.report_key ? `practical_${String(selected.id).padStart(2, '0')}_report.txt` : 'Console Output Log'}</strong>
                    </div>
                    {selected.report_content && (
                      <button
                        className="btn btn-secondary"
                        style={{ fontSize: '.72rem', padding: '4px 10px' }}
                        onClick={() => {
                          navigator.clipboard.writeText(selected.report_content)
                          alert('Report output copied to clipboard!')
                        }}
                      >
                        Copy Output
                      </button>
                    )}
                  </div>

                  {selected.report_content ? (
                    <pre
                      style={{
                        background: '#060911',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        padding: 18,
                        fontSize: '.74rem',
                        fontFamily: 'var(--font-mono)',
                        color: '#38BDF8',
                        maxHeight: 520,
                        overflowY: 'auto',
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.5,
                      }}
                    >
                      {selected.report_content}
                    </pre>
                  ) : (
                    <div style={{
                      padding: 30,
                      background: 'rgba(255,255,255,0.02)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      color: 'var(--text-secondary)',
                      fontSize: '.82rem',
                    }}>
                      <strong style={{ color: 'var(--accent)' }}>Console Verification Outcome:</strong>
                      <p style={{ marginTop: 6 }}>{selected.key_result}</p>
                      <p style={{ marginTop: 8, fontSize: '.75rem', color: 'var(--text-muted)' }}>
                        This practical logs stdout metrics and dataset tables directly to the terminal rather than writing an auxiliary report file.
                      </p>
                    </div>
                  )}
                </div>
              )}


            </div>
          ) : (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a practical to view its solution
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
