import api from './axios'

export const register = (data) => api.post('/auth/register/', data).then((res) => res.data)

export const login = (email, password) =>
  api.post('/auth/login/', { email, password }).then((res) => res.data)

export const logout = (refresh) => api.post('/auth/logout/', { refresh }).then((res) => res.data)

export const fetchMe = () => api.get('/auth/me/').then((res) => res.data)

export const verifyEmail = (uid, token) =>
  api.post('/auth/verify-email/', { uid, token }).then((res) => res.data)

export const resendVerification = (email) =>
  api.post('/auth/resend-verification/', { email }).then((res) => res.data)

export const requestPasswordReset = (email) =>
  api.post('/auth/password-reset/', { email }).then((res) => res.data)

export const confirmPasswordReset = (uid, token, newPassword) =>
  api
    .post('/auth/password-reset/confirm/', { uid, token, new_password: newPassword })
    .then((res) => res.data)
