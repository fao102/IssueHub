import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listTickets, updateTicket } from '../api/tickets'
import { extractErrorMessage } from '../api/errors'
import { PRIORITY_MAP, STATUS_OPTIONS } from '../constants/tickets'

const BOARD_PAGE_SIZE = 200

export default function KanbanBoard() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dragOverColumn, setDragOverColumn] = useState(null)
  const [draggingId, setDraggingId] = useState(null)

  useEffect(() => {
    loadTickets()
  }, [])

  function loadTickets() {
    setLoading(true)
    setError('')
    listTickets({ page_size: BOARD_PAGE_SIZE })
      .then((data) => setTickets(data.results))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }

  function handleDragStart(e, ticket) {
    e.dataTransfer.setData('text/plain', ticket.id)
    e.dataTransfer.effectAllowed = 'move'
    setDraggingId(ticket.id)
  }

  function handleDragEnd() {
    setDraggingId(null)
    setDragOverColumn(null)
  }

  function handleDragOver(e, statusValue) {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    if (dragOverColumn !== statusValue) setDragOverColumn(statusValue)
  }

  async function handleDrop(e, statusValue) {
    e.preventDefault()
    setDragOverColumn(null)
    const ticketId = e.dataTransfer.getData('text/plain')
    const ticket = tickets.find((t) => t.id === ticketId)
    if (!ticket || ticket.status === statusValue) return

    const previousTickets = tickets
    setTickets(tickets.map((t) => (t.id === ticketId ? { ...t, status: statusValue } : t)))

    try {
      await updateTicket(ticketId, { status: statusValue })
    } catch (err) {
      setTickets(previousTickets)
      setError(extractErrorMessage(err))
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

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-3 px-2">
        <h1 className="h3 mb-0">Board</h1>
        <div className="d-flex gap-2">
          <Link to="/tickets" className="btn btn-outline-secondary">
            List view
          </Link>
          <Link to="/tickets/new" className="btn btn-primary">
            New ticket
          </Link>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger py-2 mx-2" role="alert">
          {error}
        </div>
      )}

      <div className="d-flex gap-3 px-2" style={{ overflowX: 'auto' }}>
        {STATUS_OPTIONS.map((column) => {
          const columnTickets = tickets.filter((t) => t.status === column.value)
          const isDragOver = dragOverColumn === column.value

          return (
            <div
              key={column.value}
              className="flex-shrink-0"
              style={{ width: 280 }}
              onDragOver={(e) => handleDragOver(e, column.value)}
              onDragLeave={() => setDragOverColumn((prev) => (prev === column.value ? null : prev))}
              onDrop={(e) => handleDrop(e, column.value)}
            >
              <div className="d-flex align-items-center gap-2 mb-2">
                <span
                  aria-hidden="true"
                  style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: column.color, flexShrink: 0 }}
                />
                <span className="fw-semibold">{column.label}</span>
                <span className="badge text-bg-light text-muted">{columnTickets.length}</span>
              </div>

              <div
                className={`d-flex flex-column gap-2 p-2 rounded border ${isDragOver ? 'bg-body-secondary' : 'bg-body-tertiary'}`}
                style={{ minHeight: 200, maxHeight: 'calc(100vh - 220px)', overflowY: 'auto', transition: 'background-color 0.1s' }}
              >
                {columnTickets.length === 0 && (
                  <div className="text-muted small text-center py-3">No tickets</div>
                )}
                {columnTickets.map((ticket) => (
                  <Link
                    key={ticket.id}
                    to={`/tickets/${ticket.id}`}
                    draggable
                    onDragStart={(e) => handleDragStart(e, ticket)}
                    onDragEnd={handleDragEnd}
                    className="card text-decoration-none text-body"
                    style={{
                      cursor: 'grab',
                      opacity: draggingId === ticket.id ? 0.5 : 1,
                    }}
                  >
                    <div className="card-body p-2">
                      <div className="small fw-semibold mb-1">{ticket.title}</div>
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="d-inline-flex align-items-center gap-1 small text-muted">
                          <span
                            aria-hidden="true"
                            style={{
                              width: 7,
                              height: 7,
                              borderRadius: '50%',
                              backgroundColor: PRIORITY_MAP[ticket.priority]?.color,
                              flexShrink: 0,
                            }}
                          />
                          {PRIORITY_MAP[ticket.priority]?.label}
                        </span>
                        {ticket.category && (
                          <span className="badge text-bg-light text-muted small">{ticket.category.name}</span>
                        )}
                      </div>
                      <div className="small text-muted mt-1">
                        {ticket.assigned_to?.email ?? 'Unassigned'}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
