export function extractErrorMessage(error) {
  const data = error?.response?.data
  const fallbackMessage = 'The server hit an internal error while processing your request. This usually means the backend is misconfigured, most commonly around the email delivery step or the database connection.'

  if (!data) {
    if (error?.response?.status === 500) return fallbackMessage
    return error?.message || 'Something went wrong. Please try again.'
  }

  if (typeof data === 'string') {
    if (data.includes('<!doctype html>') || data.includes('<html')) {
      return fallbackMessage
    }
    return data
  }

  if (data.detail) return data.detail

  const firstKey = Object.keys(data)[0]
  if (firstKey) {
    const value = data[firstKey]
    const message = Array.isArray(value) ? value[0] : value
    return typeof message === 'string' ? message : fallbackMessage
  }

  return fallbackMessage
}
