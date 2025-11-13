import { Routes, Route, Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'

import Dashboard from './pages/Dashboard'
import Groups from './pages/Groups'
import GroupDetail from './pages/GroupDetail'
import Settings from './pages/Settings'

export function App(): ReactElement {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/groups" element={<Groups />} />
      <Route path="/groups/:id" element={<GroupDetail />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
