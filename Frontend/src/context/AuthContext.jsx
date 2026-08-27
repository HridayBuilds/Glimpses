import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import * as cognito from '../lib/cognito'

const AuthContext = createContext(null)

function userFromSession(session) {
  const payload = session.getIdToken().decodePayload()
  return { sub: payload.sub, email: payload.email, name: payload.name }
}

export function AuthProvider({ children }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    cognito.getCurrentSession().then((session) => {
      setUser(session ? userFromSession(session) : null)
      setLoading(false)
    })
  }, [])

  const login = useCallback(
    async (email, password) => {
      const session = await cognito.login(email, password)
      queryClient.clear()
      setUser(userFromSession(session))
      return session
    },
    [queryClient],
  )

  const signUp = useCallback((name, email, password) => cognito.signUp(name, email, password), [])

  const confirmSignUp = useCallback((email, code) => cognito.confirmSignUp(email, code), [])

  const resendConfirmationCode = useCallback((email) => cognito.resendConfirmationCode(email), [])

  const forgotPassword = useCallback((email) => cognito.forgotPassword(email), [])

  const confirmPassword = useCallback(
    (email, code, newPassword) => cognito.confirmPassword(email, code, newPassword),
    [],
  )

  const logout = useCallback(() => {
    cognito.signOut()
    queryClient.clear()
    setUser(null)
  }, [queryClient])

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    signUp,
    confirmSignUp,
    resendConfirmationCode,
    forgotPassword,
    confirmPassword,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
