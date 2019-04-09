/* eslint no-throw-literal: 0 */
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import api from '../api'
import {
  CREATE_MESSAGES_ERROR,
  LOAD_MESSAGES_ERROR,
  LOAD_MESSAGES_START,
  LOAD_MESSAGES_SUCCESS,
  SEND_MESSAGE_BEFORE,
  SEND_MESSAGE_ERROR,
  SEND_MESSAGE_TRYING, UNLOAD_MESSAGES_SUCCESS,
  UPDATE_MESSAGES_ERROR,
  UPDATE_MESSAGES_SUCCESS
} from './action-types'
import {
  createMessagesError,
  loadMessages,
  loadMessagesSuccess,
  sendMessage, unloadMessages,
  updateMessagesError,
  updateMessagesSuccess
} from './actions'

const middlewares = [ thunk ]
const mockStore = configureMockStore(middlewares)

describe('ACTIONS createMessageError', () => {
  it('should returns correct action type and payload', () => {
    expect(createMessagesError({ message: 'test_error' }))
      .toEqual({
        type: CREATE_MESSAGES_ERROR,
        payload: {
          message: 'test_error'
        }
      })
  })
})

describe('ACTIONS updateMessagesError', () => {
  it('should returns correct action type and payload', () => {
    expect(updateMessagesError({ message: 'test_error' }))
      .toEqual({
        type: UPDATE_MESSAGES_ERROR,
        payload: {
          message: 'test_error'
        }
      })
  })
})

describe('ACTIONS updateMessagesError', () => {
  it('should returns correct action type and payload', () => {
    expect(updateMessagesSuccess({ message: 'test_mes' }))
      .toEqual({
        type: UPDATE_MESSAGES_SUCCESS,
        payload: {
          message: 'test_mes'
        }
      })
  })
})

describe('ACTIONS loadMessageSuccess', () => {
  it('should returns correct action type and payload', () => {
    expect(loadMessagesSuccess([]))
      .toEqual({
        type: LOAD_MESSAGES_SUCCESS,
        payload: []
      })
  })
})

describe('ACTIONS loadMessages', () => {
  it('should load with api success', () => {
    const store = mockStore({})

    api.fetchMessages = async () => {
      return {
        data: {
          data: {
            conversation: {},
            messages: []
          }
        }
      }
    }

    return store.dispatch(loadMessages('123', '234'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_MESSAGES_START },
          {
            type: LOAD_MESSAGES_SUCCESS,
            payload: {
              conversation: { avatarMedium: 'undefined', avatarSmall: 'undefined' },
              messages: []
            }
          }
        ])
      })
  })

  it('should not load when api failure', () => {
    const store = mockStore({})

    api.fetchMessages = async () => {
      throw { error: 'error' }
    }
    return store.dispatch(loadMessages('123', '234'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_MESSAGES_START },
          { type: LOAD_MESSAGES_ERROR }
        ])
      })
  })
})

describe('ACTIONS unloadMessages', () => {
  it('should return correct type', () => {
    expect(unloadMessages()).toEqual({
      type: UNLOAD_MESSAGES_SUCCESS
    })
  })
})

describe('ACTIONS sendMessage', () => {

  it('should send with api success', () => {
    const store = mockStore({})

    api.sendMessage = async () => {
      return {
        data: {
          data: {
            viewerHid: '123',
            conversationId: '123'
          }
        }
      }
    }

    api.fetchMessages = async () => {
      return {
        data: {
          data: {
            conversation: {},
            messages: []
          }
        }
      }
    }

    return store.dispatch(sendMessage({ text: '123234' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: SEND_MESSAGE_TRYING },
          { type: LOAD_MESSAGES_START },
          {
            type: LOAD_MESSAGES_SUCCESS,
            payload: {
              conversation: { avatarMedium: 'undefined', avatarSmall: 'undefined' },
              messages: []
            }
          },
          { type: SEND_MESSAGE_BEFORE } ])
      })
  })

  it('should not send when api failure', async () => {
    const store = mockStore({})

    api.sendMessage = async () => {
      throw { error: 'error' }
    }
    return store.dispatch(sendMessage({ text: '123234' }))
      .then(() => {
        return new Promise(resolve => {
          setTimeout(() => {
            resolve()
          }, 3000)
        })
      })
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: SEND_MESSAGE_TRYING },
          { type: SEND_MESSAGE_ERROR, payload: { error: 'error' } },
          { type: SEND_MESSAGE_BEFORE }
        ])
        return
      })
  })
})
