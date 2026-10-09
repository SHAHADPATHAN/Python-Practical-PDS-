import React, { Component, ErrorInfo, ReactNode } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

// Global error telemetry
window.addEventListener('error', (event) => {
  const errData = {
    type: 'uncaught_error',
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    stack: event.error?.stack,
  }
  fetch('/api/client-error', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(errData),
  }).catch(() => {})
})

window.addEventListener('unhandledrejection', (event) => {
  const errData = {
    type: 'unhandled_rejection',
    message: String(event.reason),
    stack: event.reason?.stack,
  }
  fetch('/api/client-error', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(errData),
  }).catch(() => {})
})

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

class RootErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    fetch('/api/client-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'react_render_error',
        message: error.message,
        stack: error.stack,
        componentStack: info.componentStack,
      }),
    }).catch(() => {})
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#080C14',
          color: '#F8FAFC',
          padding: '40px 20px',
          fontFamily: 'system-ui, sans-serif',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{
            maxWidth: 640,
            background: 'rgba(15, 23, 40, 0.95)',
            border: '1px solid rgba(255, 87, 34, 0.4)',
            borderRadius: 12,
            padding: 30,
            boxShadow: '0 20px 40px rgba(0,0,0,0.8)',
          }}>
            <h2 style={{ color: '#FF5722', marginBottom: 12, fontSize: '1.3rem' }}>
              Interface Diagnostic Catch
            </h2>
            <p style={{ color: '#94A3B8', fontSize: '.85rem', marginBottom: 16 }}>
              A rendering exception occurred in the component hierarchy:
            </p>
            <pre style={{
              background: 'rgba(0,0,0,0.6)',
              border: '1px solid rgba(255,255,255,0.1)',
              padding: 14,
              borderRadius: 6,
              fontSize: '.75rem',
              color: '#F87171',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              overflowX: 'auto',
            }}>
              {this.state.error?.message || 'Unknown error'}
              {'\n\n'}
              {this.state.error?.stack}
            </pre>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: 20,
                background: '#FF6B00',
                border: 'none',
                color: '#fff',
                padding: '10px 20px',
                borderRadius: 6,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reload Interface
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RootErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </RootErrorBoundary>
  </React.StrictMode>,
)
