import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listCategories, listTickets } from '../api/tickets'
import { extractErrorMessage } from '../api/errors'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../constants/tickets'
import StatusBadge from '../components/StatusBadge'
import PriorityBadge from '../components/PriorityBadge'

const initialFilters = { status: '', priority: '', category: '', search: '' }

export default function TicketsList() {
  const [tickets, setTickets] = useState([])
  const [count, setCount] = useState(0)
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState(initialFilters)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    listCategories()
      .then((data) => setCategories(data.results ?? data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError('')
    const params = { page, ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)) }

    listTickets(params)
      .then((data) => {
        setTickets(data.results)
        setCount(data.count)
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [filters, page])

  function handleFilterChange(e) {
    setPage(1)
    setFilters({ ...filters, [e.target.name]: e.target.value })
  }

  const pageSize = 20
  const totalPages = Math.max(1, Math.ceil(count / pageSize))

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h3 mb-0">Tickets</h1>
        <Link to="/tickets/new" className="btn btn-primary">
          New ticket
        </Link>
      </div>

      <div className="row g-2 mb-3">
        <div className="col-md-3">
          <input
            className="form-control"
            name="search"
            placeholder="Search title or description"
            value={filters.search}
            onChange={handleFilterChange}
          />
        </div>
        <div className="col-md-3">
          <select className="form-select" name="status" value={filters.status} onChange={handleFilterChange}>
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-3">
          <select className="form-select" name="priority" value={filters.priority} onChange={handleFilterChange}>
            <option value="">All priorities</option>
            {PRIORITY_OPTIONS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-3">
          <select className="form-select" name="category" value={filters.category} onChange={handleFilterChange}>
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      <div className="table-responsive">
        <table className="table table-hover align-middle bg-white">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Category</th>
              <th>Assigned to</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="text-center py-4">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && tickets.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-4 text-muted">
                  No tickets found.
                </td>
              </tr>
            )}
            {!loading &&
              tickets.map((ticket) => (
                <tr key={ticket.id} style={{ cursor: 'pointer' }}>
                  <td>
                    <Link to={`/tickets/${ticket.id}`} className="text-decoration-none">
                      {ticket.title}
                    </Link>
                  </td>
                  <td>
                    <StatusBadge status={ticket.status} />
                  </td>
                  <td>
                    <PriorityBadge priority={ticket.priority} />
                  </td>
                  <td>{ticket.category?.name ?? '—'}</td>
                  <td>{ticket.assigned_to?.email ?? 'Unassigned'}</td>
                  <td>{new Date(ticket.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <nav className="d-flex justify-content-center">
          <ul className="pagination">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <li key={p} className={`page-item ${p === page ? 'active' : ''}`}>
                <button className="page-link" onClick={() => setPage(p)}>
                  {p}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  )
}
