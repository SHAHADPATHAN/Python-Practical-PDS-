import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'

import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Records from './pages/Records'
import IpIntelligence from './pages/IpIntelligence'
import Security from './pages/Security'
import Eda from './pages/Eda'
import Features from './pages/Features'
import Balancing from './pages/Balancing'
import Wrangling from './pages/Wrangling'
import MachineLearning from './pages/MachineLearning'
import Prediction from './pages/Prediction'
import Practicals from './pages/Practicals'
import Reports from './pages/Reports'
import Dataset from './pages/Dataset'
import Architecture from './pages/Architecture'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/records" element={<Records />} />
        <Route path="/ip-intelligence" element={<IpIntelligence />} />
        <Route path="/security" element={<Security />} />
        <Route path="/eda" element={<Eda />} />
        <Route path="/features" element={<Features />} />
        <Route path="/balancing" element={<Balancing />} />
        <Route path="/wrangling" element={<Wrangling />} />
        <Route path="/ml" element={<MachineLearning />} />
        <Route path="/prediction" element={<Prediction />} />
        <Route path="/practicals" element={<Practicals />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/dataset" element={<Dataset />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
