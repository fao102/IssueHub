import api from './axios'

export const queryRag = (payload) => api.post('/rag/query/', payload).then((res) => res.data)
