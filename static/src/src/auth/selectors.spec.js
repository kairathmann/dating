import { AuthState } from './reducer'
import * as selectors from './selectors'

describe('SELECTORS', () => {
  it('returns true if authenticated is in state', () => {

    const result = selectors.isAuthenticated({
      auth: new AuthState({
        authenticated: true
      })
    })

    expect(result).toEqual(true)
  })

  it('returns false if not authenticated is in state', () => {

    const result = selectors.isAuthenticated({
      auth: new AuthState({
        authenticated: false
      })
    })

    expect(result).toEqual(false)
  })
})
