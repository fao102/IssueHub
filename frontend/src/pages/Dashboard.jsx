import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { resendVerification } from '../api/auth'
import { extractErrorMessage } from '../api/errors'

export default function Dashboard() {
  const { user } = useAuth()
  const [resendState, setResendState] = useState('idle')
  const [error, setError] = useState('')

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

      <h1 className="h3">Welcome{user?.first_name ? `, ${user.first_name}` : ''}</h1>
      <p className="text-muted">
        This is your IssueHub dashboard. Ticket management, organisations and AI features are on
        the way.
      </p>
    </div>
  )
}
