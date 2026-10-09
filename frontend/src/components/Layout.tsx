import React from 'react'
import { NavLink, useLocation, Outlet } from 'react-router-dom'

interface NavItem {
  to: string
  icon: string
  label: string
  section?: string
}

const NAV: NavItem[] = [
  { to: '/',               icon: '⬡',  label: 'Dashboard',           section: 'OVERVIEW' },
  { to: '/upload',         icon: '↑',  label: 'Log Upload' },
  { to: '/records',        icon: '≡',  label: 'Log Records' },
  { to: '/ip-intelligence',icon: '◎',  label: 'IP Intelligence',     section: 'SECURITY' },
  { to: '/security',       icon: '⚡',  label: 'Security Intel' },
  { to: '/eda',            icon: '∿',  label: 'Data Analysis',       section: 'ANALYTICS' },
  { to: '/features',       icon: '⊕',  label: 'Feature Engineering' },
  { to: '/balancing',      icon: '⇔',  label: 'Data Balancing' },
  { to: '/wrangling',      icon: '⇄',  label: 'Data Wrangling' },
  { to: '/ml',             icon: '◆',  label: 'Machine Learning',    section: 'ML & MODEL' },
  { to: '/prediction',     icon: '▶',  label: 'Model Prediction' },
  { to: '/practicals',     icon: '◉',  label: 'Practicals',          section: 'PROJECT' },
  { to: '/reports',        icon: '📄', label: 'Reports' },
  { to: '/dataset',        icon: '🗄', label: 'Dataset' },
  { to: '/architecture',   icon: '⬡',  label: 'Architecture' },
]

export function Sidebar() {
  const location = useLocation()
  let lastSection = ''

  return (
    <aside className="sidebar">
      {/* Unique Apex Sentinel Logo */}
      <div className="sidebar-logo">
        <NavLink to="/" className="advanced-logo-link" title="Security Command Center">
          <div className="advanced-logo-badge">
            <svg
              className="advanced-logo-svg"
              width="38"
              height="38"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                {/* Left Aerodynamic Blade Gradient */}
                <linearGradient id="apexBladeLeft" x1="8" y1="5" x2="24" y2="43" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FFA24C" />
                  <stop offset="35%" stopColor="#FF6600" />
                  <stop offset="100%" stopColor="#C93400" />
                </linearGradient>

                {/* Right Aerodynamic Blade Gradient */}
                <linearGradient id="apexBladeRight" x1="40" y1="5" x2="24" y2="43" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FFBA66" />
                  <stop offset="40%" stopColor="#FF7A00" />
                  <stop offset="100%" stopColor="#9C2400" />
                </linearGradient>

                {/* Apex Crown Facet */}
                <linearGradient id="apexCrownGlint" x1="17" y1="5" x2="31" y2="13" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#FFD299" stopOpacity="0.25" />
                </linearGradient>

                {/* Floating Quantum Core - Left Facet */}
                <linearGradient id="coreFacetLeft" x1="19" y1="18" x2="24" y2="29" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#67E8F9" />
                  <stop offset="100%" stopColor="#0284C7" />
                </linearGradient>

                {/* Floating Quantum Core - Right Facet */}
                <linearGradient id="coreFacetRight" x1="29" y1="18" x2="24" y2="29" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="100%" stopColor="#38BDF8" />
                </linearGradient>

                {/* Core Luminous Aura */}
                <filter id="shardGlow" x="-40%" y="-40%" width="180%" height="180%">
                  <feGaussianBlur stdDeviation="2.5" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Left Sculpted Aerodynamic Wing */}
              <path
                d="M24 5 L8 15 V28 L24 41 V33 L14 26 V18 L24 12 Z"
                fill="url(#apexBladeLeft)"
              />

              {/* Right Sculpted Aerodynamic Wing */}
              <path
                d="M24 5 L40 15 V28 L24 41 V33 L34 26 V18 L24 12 Z"
                fill="url(#apexBladeRight)"
              />

              {/* Apex Crown Bevel Reflection */}
              <path
                d="M24 5 L17 10.5 L24 14.5 L31 10.5 Z"
                fill="url(#apexCrownGlint)"
              />

              {/* Suspended Dual-Faceted Quantum Core */}
              <g filter="url(#shardGlow)">
                <path
                  d="M24 17.5 L19 23.5 L24 29.5 Z"
                  fill="url(#coreFacetLeft)"
                />
                <path
                  d="M24 17.5 L29 23.5 L24 29.5 Z"
                  fill="url(#coreFacetRight)"
                />
              </g>
            </svg>
          </div>
        </NavLink>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {NAV.map((item) => {
          const showSection = item.section && item.section !== lastSection
          if (item.section) lastSection = item.section
          return (
            <React.Fragment key={item.to}>
              {showSection && (
                <div className="nav-section-label">{item.section}</div>
              )}
              <NavLink
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `nav-item ${isActive ? 'active' : ''}`
                }
              >
                <span style={{ fontSize: '1rem', lineHeight: 1 }}>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </React.Fragment>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid var(--border)',
        fontSize: '.65rem',
        color: 'var(--text-muted)',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}>
        <div style={{ fontFamily: 'var(--font-mono)' }}>PDS v1.0.0</div>
        <div>10 Practicals Completed</div>
      </div>
    </aside>
  )
}

export function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <div className="status-dot" />
        <span>SECURITY COMMAND</span>
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <div className="topbar-badge">
          <span style={{ color: 'var(--accent)' }}>●</span>
          <span>CJ.LOG STREAM</span>
        </div>
        <div className="topbar-badge" style={{ fontFamily: 'var(--font-mono)', fontSize: '.72rem' }}>
          2,060,520 EVENTS
        </div>
        <div className="topbar-badge" style={{ fontFamily: 'var(--font-mono)', fontSize: '.72rem', color: '#10B981' }}>
          99.96% VALID
        </div>
      </div>

      <div style={{ flex: 1 }} />

      <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
        <div style={{
          fontSize: '.72rem',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)',
          background: 'rgba(255,255,255,0.03)',
          padding: '4px 10px',
          borderRadius: 6,
          border: '1px solid var(--border)',
        }}>
          LATENCY: <span style={{ color: '#06B6D4' }}>&lt; 10ms</span>
        </div>
        <div style={{
          fontSize: '.72rem',
          fontFamily: 'var(--font-mono)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          padding: '4px 10px',
          borderRadius: 6,
          color: '#34D399',
          fontWeight: 600,
        }}>
          STATUS: ONLINE
        </div>
      </div>
    </header>
  )
}

export function Layout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Topbar />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout

