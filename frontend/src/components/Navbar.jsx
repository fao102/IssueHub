import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="navbar navbar-expand navbar-dark bg-dark px-3">
      <Link to="/" className="navbar-brand fw-semibold">
        IssueHub
      </Link>
      {isAuthenticated && (
        <div className="d-flex gap-3">
          <Link to="/dashboard" className="nav-link text-light">
            Dashboard
          </Link>
          <Link to="/tickets" className="nav-link text-light">
            Tickets
          </Link>
          <Link to="/tickets/board" className="nav-link text-light">
            Kanban Board
          </Link>
        </div>
      )}
      <div className="ms-auto d-flex align-items-center gap-3">
        {isAuthenticated ? (
          <>
            <span className="text-light small">{user?.email}</span>
            <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-outline-light btn-sm">
              Log in
            </Link>
            <Link to="/register" className="btn btn-light btn-sm">
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  )
}
