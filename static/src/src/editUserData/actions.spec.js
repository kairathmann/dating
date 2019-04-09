/* eslint no-throw-literal: 0 */
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import api from '../api'
import { ASYNC_STATES } from '../enums'
import { uploadUserImage } from './actions'
import {
  LOAD_EDIT_DATA_FOR_USER_ERROR,
  LOAD_EDIT_DATA_FOR_USER_START,
  LOAD_EDIT_DATA_FOR_USER_SUCCESS,
  UPLOAD_USER_IMAGE_DONE
} from './action-types'
import { loadEditDataForUser, startUploadingUserImage } from './actions'

const middlewares = [ thunk ]
const mockStore = configureMockStore(middlewares)

describe('ACTIONS loadEditDataForUser', () => {
  it('should modify store if api success', () => {
    const store = mockStore({})

    api.loadUserForEdit = async () => {
      return { data: { data: {} } }
    }

    return store.dispatch(loadEditDataForUser('123'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_EDIT_DATA_FOR_USER_START },
          { type: LOAD_EDIT_DATA_FOR_USER_SUCCESS, payload: {} } ])
      })
  })

  it('should modify store with error action if api failure', () => {
    const store = mockStore({})

    api.loadUserForEdit = async () => {
      throw { error: 'error' }
    }

    return store.dispatch(loadEditDataForUser('123'))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: LOAD_EDIT_DATA_FOR_USER_START },
          { type: LOAD_EDIT_DATA_FOR_USER_ERROR, payload: { error: 'error' } } ])
      })
  })
})

describe('ACTIONS startUploadingUserImage', () => {
  it('should modify store with action', () => {
    const store = mockStore({})

    store.dispatch(startUploadingUserImage())
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.DURING } } ])
      })
  })
})

describe('ACTIONS uploadUserImage', () => {
  it('should fail if uploadAvatar fail', () => {
    const store = mockStore({})

    api.uploadAvatar = async () => {
      throw { error: 'error' }
    }

    store.dispatch(uploadUserImage({ image: '1232234.png' }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.DURING } },
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.FAIL } } ])
      })
  })

  it('should success if uploadAvatar success', () => {
    const store = mockStore({})

    api.loadUserForEdit = async () => {
      return { data: { data: {} } }
    }

    api.uploadAvatar = async () => {
      return { data: { avatarUrl: '123123.png' } }
    }

    return store.dispatch(uploadUserImage({ image: '1232234.png' }, { x: 1, y: 1, width: 10, height: 10 }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.DURING } },
          { type: LOAD_EDIT_DATA_FOR_USER_START },
          { type: LOAD_EDIT_DATA_FOR_USER_SUCCESS, payload: {} },
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.BEFORE } } ])
      })
  })
})
