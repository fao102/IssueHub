import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { verifyEmail } from '../api/auth'
import { extractErrorMessage } from '../api/errors'

export default function VerifyEmail() {
  const { uid, token } = useParams()
  const [status, setStatus] = useState('pending')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let cancelled = false

    verifyEmail(uid, token)
      .then(() => {
        if (!cancelled) setStatus('success')
      })
      .catch((err) => {
        if (!cancelled) {
          setStatus('error')
          setMessage(extractErrorMessage(err))
        }
      })

    return () => {
      cancelled = true
    }
  }, [uid, token])

  return (
    <div className="container" style={{ maxWidth: 480 }}>
      <div className="card mt-5 shadow-sm">
        <div className="card-body p-4 text-center">
          {status === 'pending' && <p className="mb-0">Verifying your email…</p>}
          {status === 'success' && (
            <>
              <h1 className="h4">Email verified</h1>
              <p>Your email address has been verified successfully.</p>
              <Link to="/login" className="btn btn-primary">
                Continue to login
              </Link>
            </>
          )}
          {status === 'error' && (
            <>
              <h1 className="h4">Verification failed</h1>
              <p className="text-danger">{message}</p>
              <Link to="/login" className="btn btn-outline-primary">
                Back to login
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
