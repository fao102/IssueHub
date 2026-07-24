import api from './axios'

export const listKnowledge = (params) => api.get('/knowledge/', { params }).then((res) => res.data)

export const getKnowledge = (id) => api.get(`/knowledge/${id}/`).then((res) => res.data)

export const createKnowledge = (data) => api.post('/knowledge/', data).then((res) => res.data)

export const updateKnowledge = (id, data) => api.patch(`/knowledge/${id}/`, data).then((res) => res.data)

export const deleteKnowledge = (id) => api.delete(`/knowledge/${id}/`).then((res) => res.data)
