export function extractErrorMessage(error) {
  const data = error?.response?.data
  if (!data) return error?.message || 'Something went wrong. Please try again.'

  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const firstKey = Object.keys(data)[0]
  if (firstKey) {
    const value = data[firstKey]
    const message = Array.isArray(value) ? value[0] : value
    return typeof message === 'string' ? message : 'Something went wrong. Please try again.'
  }

  return 'Something went wrong. Please try again.'
}
