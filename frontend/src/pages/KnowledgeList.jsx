import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listKnowledge } from '../api/knowledge'
import { extractErrorMessage } from '../api/errors'
import { useAuth } from '../hooks/useAuth'

const SOURCE_LABELS = { article: 'Article', ticket: 'Ticket', faq: 'FAQ' }

export default function KnowledgeList() {
  const { user } = useAuth()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    listKnowledge()
      .then((data) => setEntries(data.results ?? data))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h3 mb-0">Knowledge base</h1>
        {user?.is_staff && (
          <Link to="/knowledge/new" className="btn btn-primary">
            New article
          </Link>
        )}
      </div>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : entries.length === 0 ? (
        <p className="text-muted">No knowledge articles yet.</p>
      ) : (
        <div className="list-group">
          {entries.map((entry) => (
            <Link
              key={entry.id}
              to={`/knowledge/${entry.id}/edit`}
              className="list-group-item list-group-item-action"
            >
              <div className="d-flex justify-content-between align-items-center">
                <span className="fw-semibold">{entry.title}</span>
                <span className="badge text-bg-light text-muted">
                  {SOURCE_LABELS[entry.source_type] ?? entry.source_type}
                </span>
              </div>
              <div className="small text-muted text-truncate">{entry.content}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
