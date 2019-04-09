/* eslint no-throw-literal: 0 */
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import api from '../api'
import { UNLOAD_USER_SUCCESS } from '../user/action-types'
import * as ACTIONS from './action-types'
import {
  clearLastError, forgotPassword,
  forgotPasswordError,
  forgotPasswordSuccess,
  initAuth,
  signInError,
  signInLocal,
  signInLocalError,
  signInLocalSuccess,
  signInSuccess, signOut,
  signOutSuccess,
  signUp,
  signUpError,
  signUpSuccess
} from './actions'

const middlewares = [ thunk ]
const mockStore = configureMockStore(middlewares)

describe('ACTIONS initAuth', () => {
  it('should returns correct action type and payload', () => {
    expect(initAuth({ name: 'test_name', email: 'email@test.com' }))
      .toEqual({
        type: ACTIONS.INIT_AUTH,
        payload: {
          name: 'test_name',
          email: 'email@test.com'
        }
      })
  })
})

describe('ACTIONS signInError', () => {
  it('should returns correct action type and payload if result with user', () => {
    expect(signInError())
      .toEqual({
        type: ACTIONS.SIGN_IN_ERROR
      })
  })
})

describe('ACTIONS signInSuccess', () => {
  it('should returns correct action type and payload if result with user', () => {
    expect(signInSuccess({ user: { name: 'test_name', email: 'email@test.com' } }))
      .toEqual({
        type: ACTIONS.SIGN_IN_SUCCESS,
        payload: {
          name: 'test_name',
          email: 'email@test.com'
        }
      })
  })
  it('should returns correct action type and empty payload if result without user', () => {
    expect(signInSuccess({ name: 'test_name', email: 'email@test.com' }))
      .toEqual({
        type: ACTIONS.SIGN_IN_SUCCESS
      })
  })
})

describe('ACTIONS signInLocalSuccess', () => {
  it('should returns correct action type and payload if result with data', () => {
    expect(signInLocalSuccess({ data: { name: 'test_name', email: 'email@test.com' } }))
      .toEqual({
        type: ACTIONS.SIGN_IN_LOCAL_SUCCESS,
        payload: {
          name: 'test_name',
          email: 'email@test.com'
        }
      })
  })
  it('should returns correct action type and empty payload if result without user', () => {
    expect(signInLocalSuccess({ name: 'test_name', email: 'email@test.com' }))
      .toEqual({
        type: ACTIONS.SIGN_IN_LOCAL_SUCCESS
      })
  })
})

describe('ACTIONS signInLocalError', () => {
  it('should returns correct action type and payload if result with user', () => {
    expect(signInLocalError())
      .toEqual({
        type: ACTIONS.SIGN_IN_LOCAL_ERROR
      })
  })
})

describe('ACTIONS signUpError', () => {
  it('should return correct action type and payload if message is string', () => {
    expect(signUpError('test_error_message'))
      .toEqual({
        type: ACTIONS.SIGN_UP_ERROR,
        payload: 'test_error_message'
      })
  })

  it('should return correct action type and payload if message is object', () => {
    expect(signUpError({ code: 'test_error_message' }))
      .toEqual({
        type: ACTIONS.SIGN_UP_ERROR,
        payload: 'test_error_message'
      })
  })
})

describe('ACTIONS signUpSuccess', () => {
  it('should returns correct action type and payload if result with data', () => {
    expect(signUpSuccess({ data: { name: 'test_name', email: 'email@test.com' } }))
      .toEqual({
        type: ACTIONS.SIGN_UP_SUCCESS,
        payload: {
          name: 'test_name',
          email: 'email@test.com'
        }
      })
  })
  it('should returns correct action type and empty payload if result without user', () => {
    expect(signUpSuccess({ name: 'test_name', email: 'email@test.com' }))
      .toEqual({
        type: ACTIONS.SIGN_UP_SUCCESS
      })
  })
})

describe('ACTIONS signOutSuccess', () => {
  it('should returns correct action type', () => {
    expect(signOutSuccess())
      .toEqual({
        type: ACTIONS.SIGN_OUT_SUCCESS
      })
  })
})

describe('ACTIONS clearLastError', () => {
  it('should returns correct action type', () => {
    expect(clearLastError())
      .toEqual({
        type: ACTIONS.CLEAR_LAST_ERROR
      })
  })
})

describe('ACTIONS signUp', () => {
  it('should sign up with success', () => {
    const store = mockStore({})

    api.signup = async () => {
      return { data: { success: true } }
    }

    const redirect = jest.fn()

    return store.dispatch(signUp({ pass: '123', email: '1123' }, redirect))
      .then(() => {
        expect(store.getActions()).toEqual([ { type: ACTIONS.SIGN_UP_SUCCESS } ])
        expect(redirect.mock.calls.length).toEqual(1)
      })
  })

  it('should sign up with success and no redirect called if not passed', () => {
    const store = mockStore({})

    api.signup = async () => {
      return { data: { success: true } }
    }

    const redirect = jest.fn()

    return store.dispatch(signUp({ pass: '123', email: '1123' }, null))
      .then(() => {
        expect(store.getActions()).toEqual([ { type: ACTIONS.SIGN_UP_SUCCESS } ])
        expect(redirect.mock.calls.length).toEqual(0)
      })
  })

  it('should not sign up with api failed and plain error', () => {
    const store = mockStore({})

    api.signup = async () => {
      throw 'failed_response'
    }

    return store.dispatch(signUp({ pass: '123', email: '1123' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.SIGN_UP_ERROR, payload: 'failed_response' } ])
      })
  })

  it('should not sign up with api failed and error in object', () => {
    const store = mockStore({})

    api.signup = async () => {
      throw { response: { data: 'nested_error' } }
    }

    return store.dispatch(signUp({ pass: '123', email: '1123' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.SIGN_UP_ERROR, payload: 'nested_error' } ])
      })
  })
})

describe('ACTIONS signInLocal', () => {
  it('should sign in with api success', () => {
    const store = mockStore({})

    api.signin = async () => {
      return { data: { data: { reactivated: true } } }
    }

    return store.dispatch(signInLocal({ pass: '123', email: '1123' }))
      .then((result) => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.SIGN_IN_LOCAL_SUCCESS, payload: { reactivated: true } } ])
        expect(result).toEqual(true)
      })
  })

  it('should not sign in with api failed and plain error', () => {
    const store = mockStore({})

    api.signin = async () => {
      throw 'failed_response'
    }

    return store.dispatch(signInLocal({ pass: '123', email: '1123' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.SIGN_IN_LOCAL_ERROR, payload: 'failed_response' } ])
      })
  })

  it('should not sign up with api failed and error in object', () => {
    const store = mockStore({})

    api.signin = async () => {
      throw { response: { data: 'nested_error' } }
    }

    return store.dispatch(signInLocal({ pass: '123', email: '1123' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.SIGN_IN_LOCAL_ERROR, payload: 'nested_error' } ])
      })
  })
})

describe('ACTIONS forgotPasswordError', () => {
  it('should returns correct action type and payload if result with user', () => {
    expect(forgotPasswordError('error'))
      .toEqual({
        type: ACTIONS.FORGOT_PASSWORD_ERROR,
        payload: 'error'
      })
  })
})

describe('ACTIONS forgotPasswordSuccess', () => {
  it('should returns correct action type and payload if result with user', () => {
    expect(forgotPasswordSuccess({ data: { field: 'test' } }))
      .toEqual({
        type: ACTIONS.FORGOT_PASSWORD_SUCCESS,
        payload: {
          field: 'test'
        }
      })
  })
})

describe('ACTIONS forgotPassword', () => {
  it('should not forgot password with api success field false', () => {
    const store = mockStore({})

    api.forgotPassword = async () => {
      return { data : { success: false }}
    }

    return store.dispatch(forgotPassword('test_email@email'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.FORGOT_PASSWORD_ERROR, payload: { success: false } } ])
      })
  })

  it('should forgot password with api success field true', () => {
    const store = mockStore({})

    api.forgotPassword = async () => {
      return { data : { success: true }}
    }

    return store.dispatch(forgotPassword('test_email@email'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.FORGOT_PASSWORD_SUCCESS, payload: { success: true } } ])
      })
  })

  it('should not sign in with api failed and plain error', () => {
    const store = mockStore({})

    api.forgotPassword = async () => {
      throw 'failed_response'
    }

    return store.dispatch(forgotPassword('test_email@email'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.FORGOT_PASSWORD_ERROR, payload: 'failed_response' } ])
      })
  })

  it('should not sign up with api failed and error in object', () => {
    const store = mockStore({})

    api.forgotPassword = async () => {
      throw { response: { data: 'nested_error' } }
    }

    return store.dispatch(forgotPassword('test_email@email'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: ACTIONS.FORGOT_PASSWORD_ERROR, payload: 'nested_error' } ])
      })
  })
})

describe('ACTIONS signOut', () => {
  it('should sign out with api success', () => {
    const store = mockStore({})

    api.logout = async () => {
      return { data: {}}
    }

    return store.dispatch(signOut())
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: UNLOAD_USER_SUCCESS },
          { type: ACTIONS.SIGN_OUT_SUCCESS } ])
      })
  })

  it('shouldnt sign out with api failed and plain error', () => {
    const store = mockStore({})

    api.logout = async () => {
      throw 'error'
    }

    return store.dispatch(signOut())
      .then(() => {
        expect(store.getActions()).toEqual([])
      })
  })

})


