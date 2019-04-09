/* eslint no-throw-literal: 0 */
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import api from '../api'
import {
  LOAD_CONVERSATIONS_ERROR,
  LOAD_CONVERSATIONS_START,
  LOAD_CONVERSATIONS_SUCCESS,
  UNLOAD_CONVERSATIONS
} from './action-types'
import { loadConversations, unloadConversations } from './actions'

const middlewares = [ thunk ]
const mockStore = configureMockStore(middlewares)

describe('ACTIONS unloadConversations', () => {
  it('should returns correct action type and payload', () => {
    const result = unloadConversations()
    expect(typeof unloadConversations).toEqual('function')
    expect(result).toEqual({
      type: UNLOAD_CONVERSATIONS
    })
  })
})

describe('ACTIONS loadConversations', () => {
  it('should load conversations with api success', () => {
    const store = mockStore({})

    api.fetchConversations = async () => {
      return { data: { data: { conversations: [] } } }
    }

    return store.dispatch(loadConversations('123'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_CONVERSATIONS_START },
          { type: LOAD_CONVERSATIONS_SUCCESS, payload: [] } ])
      })
  })

  it('should load conversations with api success and process data', () => {
    const store = mockStore({})

    api.fetchConversations = async () => {
      return {
        data: {
          data: {
            conversations: [
              {
                partnerGender: 1,
                partnerAvatarSmall: 'hydra/img/src/',
                partnerAvatarMedium: 'hydra/img/src/'
              }
            ]
          }
        }
      }
    }

    return store.dispatch(loadConversations('123'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_CONVERSATIONS_START },
          {
            type: LOAD_CONVERSATIONS_SUCCESS,
            payload: [
              {
                partnerGender: 1,
                avatarSmall: 'default_male',
                avatarMedium: 'default_male'
              }
            ]
          } ])
      })
  })

  it('should not load conversations with api failure', () => {
    const store = mockStore({})

    api.fetchConversations = async () => {
      throw { code: 'error' }
    }

    return store.dispatch(loadConversations('123'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_CONVERSATIONS_START },
          { type: LOAD_CONVERSATIONS_ERROR } ])
      })
  })
})
