import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { resendVerification } from '../api/auth'
import { getDashboard } from '../api/tickets'
import { extractErrorMessage } from '../api/errors'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../constants/tickets'
import StatTile from '../components/StatTile'
import BreakdownBars from '../components/BreakdownBars'
import StatusBadge from '../components/StatusBadge'

export default function Dashboard() {
  const { user } = useAuth()
  const [resendState, setResendState] = useState('idle')
  const [error, setError] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  async function handleResend() {
    setError('')
    setResendState('sending')
    try {
      await resendVerification(user.email)
      setResendState('sent')
    } catch (err) {
      setError(extractErrorMessage(err))
      setResendState('idle')
    }
  }

  return (
    <div className="container py-4">
      {user && !user.is_email_verified && (
        <div className="alert alert-warning d-flex justify-content-between align-items-center">
          <span>Please verify your email address to unlock all features.</span>
          <button
            className="btn btn-sm btn-outline-dark"
            onClick={handleResend}
            disabled={resendState === 'sending' || resendState === 'sent'}
          >
            {resendState === 'sent' ? 'Email sent' : resendState === 'sending' ? 'Sending…' : 'Resend email'}
          </button>
        </div>
      )}
      {error && <div className="alert alert-danger py-2">{error}</div>}

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">Welcome{user?.first_name ? `, ${user.first_name}` : ''}</h1>
        <Link to="/tickets/new" className="btn btn-primary">
          New ticket
        </Link>
      </div>

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}

      {!loading && data && (
        <>
          <div className="row g-3 mb-4">
            <div className="col-6 col-md-3">
              <StatTile label="Total tickets" value={data.total} />
            </div>
            {STATUS_OPTIONS.map((s) => (
              <div className="col-6 col-md-3" key={s.value}>
                <StatTile label={s.label} value={data.by_status[s.value] || 0} color={s.color} />
              </div>
            ))}
          </div>

          <div className="row g-3 mb-4">
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header">Tickets by status</div>
                <div className="card-body">
                  <BreakdownBars options={STATUS_OPTIONS} counts={data.by_status} total={data.total} />
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header">Tickets by priority</div>
                <div className="card-body">
                  <BreakdownBars options={PRIORITY_OPTIONS} counts={data.by_priority} total={data.total} />
                </div>
              </div>
            </div>
          </div>

          <div className="row g-3">
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header">Recent tickets</div>
                <ul className="list-group list-group-flush">
                  {data.recent_tickets.length === 0 && (
                    <li className="list-group-item text-muted">No tickets yet.</li>
                  )}
                  {data.recent_tickets.map((ticket) => (
                    <li key={ticket.id} className="list-group-item d-flex justify-content-between align-items-center">
                      <Link to={`/tickets/${ticket.id}`} className="text-decoration-none">
                        {ticket.title}
                      </Link>
                      <StatusBadge status={ticket.status} />
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card h-100">
                <div className="card-header">Recent activity</div>
                <ul className="list-group list-group-flush">
                  {data.recent_activity.length === 0 && (
                    <li className="list-group-item text-muted">No activity yet.</li>
                  )}
                  {data.recent_activity.map((entry) => (
                    <li key={entry.id} className="list-group-item">
                      <div className="small text-muted">
                        {entry.actor?.email ?? 'System'} &middot; {new Date(entry.created_at).toLocaleString()}
                      </div>
                      <Link to={`/tickets/${entry.ticket_id}`} className="text-decoration-none">
                        {entry.detail}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
