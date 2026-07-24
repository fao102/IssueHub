import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import VerifyEmail from './pages/VerifyEmail'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Dashboard from './pages/Dashboard'
import TicketsList from './pages/TicketsList'
import TicketDetail from './pages/TicketDetail'
import TicketForm from './pages/TicketForm'
import KanbanBoard from './pages/KanbanBoard'
import KnowledgeList from './pages/KnowledgeList'
import KnowledgeForm from './pages/KnowledgeForm'

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email/:uid/:token" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tickets" element={<TicketsList />} />
            <Route path="/tickets/board" element={<KanbanBoard />} />
            <Route path="/tickets/new" element={<TicketForm />} />
            <Route path="/tickets/:id" element={<TicketDetail />} />
            <Route path="/tickets/:id/edit" element={<TicketForm />} />
            <Route path="/knowledge" element={<KnowledgeList />} />
            <Route path="/knowledge/new" element={<KnowledgeForm />} />
            <Route path="/knowledge/:id/edit" element={<KnowledgeForm />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}
