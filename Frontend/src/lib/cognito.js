import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from 'amazon-cognito-identity-js'

export const userPool = new CognitoUserPool({
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
})

export function signUp(name, email, password) {
  return new Promise((resolve, reject) => {
    userPool.signUp(
      email,
      password,
      [new CognitoUserAttribute({ Name: 'name', Value: name })],
      null,
      (err, result) => (err ? reject(err) : resolve(result)),
    )
  })
}

export function confirmSignUp(email, code) {
  const user = new CognitoUser({ Username: email, Pool: userPool })
  return new Promise((resolve, reject) => {
    user.confirmRegistration(code, true, (err, result) => (err ? reject(err) : resolve(result)))
  })
}

export function resendConfirmationCode(email) {
  const user = new CognitoUser({ Username: email, Pool: userPool })
  return new Promise((resolve, reject) => {
    user.resendConfirmationCode((err, result) => (err ? reject(err) : resolve(result)))
  })
}

export function login(email, password) {
  const user = new CognitoUser({ Username: email, Pool: userPool })
  const authDetails = new AuthenticationDetails({ Username: email, Password: password })
  return new Promise((resolve, reject) => {
    user.authenticateUser(authDetails, {
      onSuccess: (session) => resolve(session),
      onFailure: (err) => reject(err),
    })
  })
}

export function forgotPassword(email) {
  const user = new CognitoUser({ Username: email, Pool: userPool })
  return new Promise((resolve, reject) => {
    user.forgotPassword({
      onSuccess: (result) => resolve(result),
      onFailure: (err) => reject(err),
    })
  })
}

export function confirmPassword(email, code, newPassword) {
  const user = new CognitoUser({ Username: email, Pool: userPool })
  return new Promise((resolve, reject) => {
    user.confirmPassword(code, newPassword, {
      onSuccess: () => resolve(),
      onFailure: (err) => reject(err),
    })
  })
}

export function signOut() {
  const user = userPool.getCurrentUser()
  if (user) user.signOut()
}

// Resolves the current session, transparently refreshing an expired access
// token via the stored refresh token (built into getSession). Resolves null
// if there is no signed-in user or the refresh token itself is invalid/expired.
export function getCurrentSession() {
  const user = userPool.getCurrentUser()
  if (!user) return Promise.resolve(null)
  return new Promise((resolve) => {
    user.getSession((err, session) => {
      if (err || !session || !session.isValid()) return resolve(null)
      resolve(session)
    })
  })
}

// Forces a refresh using the stored refresh token, bypassing the cached
// session — used by the axios interceptor's 401 retry path.
export function refreshCurrentSession() {
  const user = userPool.getCurrentUser()
  if (!user) return Promise.resolve(null)
  return new Promise((resolve) => {
    user.getSession((err, session) => {
      if (err || !session) return resolve(null)
      const refreshToken = session.getRefreshToken()
      user.refreshSession(refreshToken, (refreshErr, newSession) => {
        if (refreshErr || !newSession) return resolve(null)
        resolve(newSession)
      })
    })
  })
}
