import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { deleteTicket, getAssignableUsers, getTicket, updateTicket } from '../api/tickets'
import { queryRag } from '../api/rag'
import { extractErrorMessage } from '../api/errors'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../constants/tickets'
import { useAuth } from '../hooks/useAuth'
import StatusBadge from '../components/StatusBadge'
import PriorityBadge from '../components/PriorityBadge'

export default function TicketDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [ticket, setTicket] = useState(null)
  const [assignableUsers, setAssignableUsers] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [assistantQuestion, setAssistantQuestion] = useState('')
  const [assistantAnswer, setAssistantAnswer] = useState('')
  const [assistantSources, setAssistantSources] = useState([])
  const [assistantConfigured, setAssistantConfigured] = useState(true)
  const [assistantAsked, setAssistantAsked] = useState(false)
  const [assistantLoading, setAssistantLoading] = useState(false)

  useEffect(() => {
    loadTicket()
    if (user?.is_staff) {
      getAssignableUsers()
        .then(setAssignableUsers)
        .catch(() => {})
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, user])

  function loadTicket() {
    setLoading(true)
    setError('')
    getTicket(id)
      .then(setTicket)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }

  async function handleFieldUpdate(field, value) {
    setUpdating(true)
    setError('')
    try {
      await updateTicket(id, { [field]: value || null })
      // Re-fetch the full detail (with activity) rather than using the
      // PATCH response, which comes back via the lighter list serializer.
      const refreshed = await getTicket(id)
      setTicket(refreshed)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setUpdating(false)
    }
  }

  async function handleDelete() {
    if (!window.confirm('Delete this ticket? This cannot be undone.')) return
    try {
      await deleteTicket(id)
      navigate('/tickets')
    } catch (err) {
      setError(extractErrorMessage(err))
    }
  }

  async function handleAssistantSubmit(e) {
    e.preventDefault()
    if (!assistantQuestion.trim()) return

    setAssistantLoading(true)
    setAssistantAnswer('')
    setAssistantSources([])
    setAssistantAsked(true)
    try {
      const result = await queryRag({ question: assistantQuestion, ticket_id: id })
      setAssistantAnswer(result.answer)
      setAssistantSources(result.sources || [])
      setAssistantConfigured(result.configured !== false)
    } catch (err) {
      setAssistantAnswer(extractErrorMessage(err))
      setAssistantConfigured(true)
    } finally {
      setAssistantLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container py-4 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  if (error && !ticket) {
    return (
      <div className="container py-4">
        <div className="alert alert-danger">{error}</div>
        <Link to="/tickets">Back to tickets</Link>
      </div>
    )
  }

  return (
    <div className="container py-4">
      <Link to="/tickets" className="d-inline-block mb-3">
        &larr; Back to tickets
      </Link>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      <div className="row">
        <div className="col-lg-8">
          <div className="card mb-3">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start">
                <h1 className="h4">{ticket.title}</h1>
                <div className="d-flex gap-2">
                  <Link to={`/tickets/${id}/edit`} className="btn btn-sm btn-outline-secondary">
                    Edit
                  </Link>
                  <button className="btn btn-sm btn-outline-danger" onClick={handleDelete}>
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-muted small mb-3">
                Opened by {ticket.created_by.email} on {new Date(ticket.created_at).toLocaleString()}
              </p>
              <p style={{ whiteSpace: 'pre-wrap' }}>{ticket.description || 'No description provided.'}</p>
            </div>
          </div>

          <div className="card mb-3">
            <div className="card-header">AI Assistant</div>
            <div className="card-body">
              <form onSubmit={handleAssistantSubmit} className="d-flex gap-2 mb-3">
                <input
                  className="form-control"
                  value={assistantQuestion}
                  onChange={(e) => setAssistantQuestion(e.target.value)}
                  placeholder="Ask about this ticket or related knowledge"
                />
                <button className="btn btn-primary" type="submit" disabled={assistantLoading}>
                  {assistantLoading ? 'Thinking...' : 'Ask'}
                </button>
              </form>

              {assistantAsked && !assistantConfigured && (
                <div className="alert alert-info py-2 small" role="status">
                  No AI answer-generation model is configured, so the assistant is returning the most
                  relevant knowledge-base excerpts instead of a generated answer. See{' '}
                  <code>docs/RAG_SETUP.md</code> to wire up a provider key.
                </div>
              )}

              {assistantAnswer && (
                <div>
                  <div className="fw-semibold mb-2">Answer</div>
                  <div className="border rounded p-3 bg-light" style={{ whiteSpace: 'pre-wrap' }}>
                    {assistantAnswer}
                  </div>
                  {assistantSources.length > 0 && (
                    <div className="mt-3">
                      <div className="fw-semibold mb-2">Sources</div>
                      <ul className="mb-0">
                        {assistantSources.map((source) => (
                          <li key={source.id}>
                            <strong>{source.title}</strong> <span className="text-muted">({source.source_type})</span>
                            <div className="small text-muted">{source.content}</div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">Activity</div>
            <ul className="list-group list-group-flush">
              {ticket.activity.length === 0 && (
                <li className="list-group-item text-muted">No activity yet.</li>
              )}
              {ticket.activity.map((entry) => (
                <li key={entry.id} className="list-group-item">
                  <div className="small text-muted">
                    {entry.actor?.email ?? 'System'} &middot; {new Date(entry.created_at).toLocaleString()}
                  </div>
                  <div>{entry.detail}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card">
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label small text-muted" htmlFor="ticket-status">
                  Status
                </label>
                <select
                  id="ticket-status"
                  className="form-select"
                  value={ticket.status}
                  disabled={updating}
                  onChange={(e) => handleFieldUpdate('status', e.target.value)}
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label}
                    </option>
                  ))}
                </select>
                <div className="mt-1">
                  <StatusBadge status={ticket.status} />
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label small text-muted" htmlFor="ticket-priority">
                  Priority
                </label>
                <select
                  id="ticket-priority"
                  className="form-select"
                  value={ticket.priority}
                  disabled={updating}
                  onChange={(e) => handleFieldUpdate('priority', e.target.value)}
                >
                  {PRIORITY_OPTIONS.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <div className="mt-1">
                  <PriorityBadge priority={ticket.priority} />
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label small text-muted">Category</label>
                <div>{ticket.category?.name ?? 'None'}</div>
              </div>

              <div className="mb-0">
                <label className="form-label small text-muted" htmlFor="ticket-assigned-to">
                  Assigned to
                </label>
                {user?.is_staff ? (
                  <select
                    id="ticket-assigned-to"
                    className="form-select"
                    value={ticket.assigned_to?.id ?? ''}
                    disabled={updating}
                    onChange={(e) => handleFieldUpdate('assigned_to_id', e.target.value)}
                  >
                    <option value="">Unassigned</option>
                    {assignableUsers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.email}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div>{ticket.assigned_to?.email ?? 'Unassigned'}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
