import api from './axios'

export const listTickets = (params) => api.get('/tickets/', { params }).then((res) => res.data)

export const getTicket = (id) => api.get(`/tickets/${id}/`).then((res) => res.data)

export const createTicket = (data) => api.post('/tickets/', data).then((res) => res.data)

export const updateTicket = (id, data) => api.patch(`/tickets/${id}/`, data).then((res) => res.data)

export const deleteTicket = (id) => api.delete(`/tickets/${id}/`).then((res) => res.data)

export const listCategories = () => api.get('/categories/').then((res) => res.data)

export const createCategory = (name) => api.post('/categories/', { name }).then((res) => res.data)

export const getAssignableUsers = () => api.get('/tickets/assignable-users/').then((res) => res.data)

export const getDashboard = () => api.get('/tickets/dashboard/').then((res) => res.data)
