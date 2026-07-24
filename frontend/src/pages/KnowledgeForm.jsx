import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  createKnowledge,
  deleteKnowledge,
  getKnowledge,
  updateKnowledge,
} from '../api/knowledge'
import { extractErrorMessage } from '../api/errors'
import { useAuth } from '../hooks/useAuth'

const SOURCE_OPTIONS = [
  { value: 'article', label: 'Article' },
  { value: 'faq', label: 'FAQ' },
  { value: 'ticket', label: 'Ticket' },
]

const emptyForm = { title: '', content: '', source_type: 'article' }

export default function KnowledgeForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const { user } = useAuth()

  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!isEdit) return
    getKnowledge(id)
      .then((entry) =>
        setForm({ title: entry.title, content: entry.content, source_type: entry.source_type }),
      )
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [id, isEdit])

  if (!user?.is_staff) {
    return (
      <div className="container py-4">
        <div className="alert alert-warning">Only staff can manage knowledge articles.</div>
        <Link to="/knowledge">Back to knowledge base</Link>
      </div>
    )
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const entry = isEdit ? await updateKnowledge(id, form) : await createKnowledge(form)
      navigate('/knowledge', { state: { savedId: entry.id } })
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete() {
    if (!window.confirm('Delete this article? This cannot be undone.')) return
    try {
      await deleteKnowledge(id)
      navigate('/knowledge')
    } catch (err) {
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
    <div className="container py-4" style={{ maxWidth: 720 }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">{isEdit ? 'Edit article' : 'New article'}</h1>
        {isEdit && (
          <button className="btn btn-outline-danger btn-sm" onClick={handleDelete}>
            Delete
          </button>
        )}
      </div>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Title</label>
          <input className="form-control" name="title" value={form.title} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Source type</label>
          <select
            className="form-select"
            name="source_type"
            value={form.source_type}
            onChange={handleChange}
          >
            {SOURCE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Content</label>
          <textarea
            className="form-control"
            name="content"
            rows={10}
            value={form.content}
            onChange={handleChange}
            required
          />
          <div className="form-text">
            This text is chunked and embedded for retrieval when users ask the AI assistant.
          </div>
        </div>
        <div className="d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving…' : isEdit ? 'Save changes' : 'Create article'}
          </button>
          <Link to="/knowledge" className="btn btn-outline-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  )
}
