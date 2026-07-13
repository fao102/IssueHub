import { createContext, useCallback, useEffect, useState } from 'react'
import { tokenStorage } from '../api/axios'
import * as authApi from '../api/auth'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadUser() {
      if (tokenStorage.getAccess()) {
        try {
          const me = await authApi.fetchMe()
          setUser(me)
        } catch {
          tokenStorage.clear()
        }
      }
      setLoading(false)
    }
    loadUser()
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password)
    tokenStorage.setTokens(data.access, data.refresh)
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (payload) => {
    const data = await authApi.register(payload)
    tokenStorage.setTokens(data.access, data.refresh)
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(async () => {
    const refresh = tokenStorage.getRefresh()
    if (refresh) {
      try {
        // Must run before clearing tokens - the request needs the access
        // token still attached to authenticate against the logout endpoint.
        await authApi.logout(refresh)
      } catch {
        // Token may already be expired/blacklisted - clear local state anyway.
      }
    }
    tokenStorage.clear()
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const me = await authApi.fetchMe()
    setUser(me)
    return me
  }, [])

  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
