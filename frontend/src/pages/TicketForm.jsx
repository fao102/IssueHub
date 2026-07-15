import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  createCategory,
  createTicket,
  getAssignableUsers,
  getTicket,
  listCategories,
  updateTicket,
} from '../api/tickets'
import { extractErrorMessage } from '../api/errors'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../constants/tickets'
import { useAuth } from '../hooks/useAuth'

const emptyForm = {
  title: '',
  description: '',
  category_id: '',
  priority: 'medium',
  status: 'open',
  assigned_to_id: '',
}

export default function TicketForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const { user } = useAuth()

  const [form, setForm] = useState(emptyForm)
  const [categories, setCategories] = useState([])
  const [assignableUsers, setAssignableUsers] = useState([])
  const [newCategoryName, setNewCategoryName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    listCategories()
      .then((data) => setCategories(data.results ?? data))
      .catch(() => {})

    if (user?.is_staff) {
      getAssignableUsers()
        .then(setAssignableUsers)
        .catch(() => {})
    }
  }, [user])

  useEffect(() => {
    if (!isEdit) return
    getTicket(id)
      .then((ticket) => {
        setForm({
          title: ticket.title,
          description: ticket.description,
          category_id: ticket.category?.id ?? '',
          priority: ticket.priority,
          status: ticket.status,
          assigned_to_id: ticket.assigned_to?.id ?? '',
        })
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [id, isEdit])

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleAddCategory() {
    if (!newCategoryName.trim()) return
    try {
      const category = await createCategory(newCategoryName.trim())
      setCategories([...categories, category])
      setForm({ ...form, category_id: category.id })
      setNewCategoryName('')
    } catch (err) {
      setError(extractErrorMessage(err))
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    const payload = {
      title: form.title,
      description: form.description,
      category_id: form.category_id || null,
      priority: form.priority,
    }
    if (isEdit) {
      payload.status = form.status
      if (user?.is_staff) {
        payload.assigned_to_id = form.assigned_to_id || null
      }
    }

    try {
      const ticket = isEdit ? await updateTicket(id, payload) : await createTicket(payload)
      navigate(`/tickets/${ticket.id}`)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setSubmitting(false)
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
    <div className="container py-4" style={{ maxWidth: 640 }}>
      <h1 className="h3 mb-4">{isEdit ? 'Edit ticket' : 'New ticket'}</h1>
      {error && <div className="alert alert-danger py-2">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Title</label>
          <input className="form-control" name="title" value={form.title} onChange={handleChange} required />
        </div>

        <div className="mb-3">
          <label className="form-label">Description</label>
          <textarea
            className="form-control"
            name="description"
            rows={4}
            value={form.description}
            onChange={handleChange}
          />
        </div>

        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">Category</label>
            <select className="form-select" name="category_id" value={form.category_id} onChange={handleChange}>
              <option value="">No category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <div className="input-group input-group-sm mt-2">
              <input
                className="form-control"
                placeholder="New category name"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
              />
              <button type="button" className="btn btn-outline-secondary" onClick={handleAddCategory}>
                Add
              </button>
            </div>
          </div>

          <div className="col-md-6 mb-3">
            <label className="form-label">Priority</label>
            <select className="form-select" name="priority" value={form.priority} onChange={handleChange}>
              {PRIORITY_OPTIONS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {isEdit && (
          <div className="row">
            <div className="col-md-6 mb-3">
              <label className="form-label">Status</label>
              <select className="form-select" name="status" value={form.status} onChange={handleChange}>
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            {user?.is_staff && (
              <div className="col-md-6 mb-3">
                <label className="form-label">Assigned to</label>
                <select
                  className="form-select"
                  name="assigned_to_id"
                  value={form.assigned_to_id}
                  onChange={handleChange}
                >
                  <option value="">Unassigned</option>
                  {assignableUsers.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.email}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : isEdit ? 'Save changes' : 'Create ticket'}
        </button>
      </form>
    </div>
  )
}
