/* eslint no-throw-literal: 0 */
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import api from '../api'
import { ASYNC_STATES } from '../enums'
import { START_FILL_DATA, UPDATE_DATA, UPLOAD_USER_IMAGE_DONE } from './action-types'
import { saveChanges, startFillData, startUploadingUserImage, updateUser, uploadUserImage } from './actions'
import * as userActions from '../user/actions'

const middlewares = [ thunk ]
const mockStore = configureMockStore(middlewares)

describe('ACTIONS updateUser', () => {
  it('should modify store', () => {
    const store = mockStore({})

    store.dispatch(updateUser({ firstName: '123' }))
    expect(store.getActions()).toEqual([
      { type: UPDATE_DATA, payload: { firstName: '123' } }
    ])
  })
})

describe('ACTIONS startFillData', () => {
  it('should modify store with action', () => {
    const store = mockStore({})

    store.dispatch(startFillData())
    expect(store.getActions()).toEqual([
      { type: START_FILL_DATA, payload: {} }
    ])
  })
})

describe('ACTIONS saveChanges', () => {
  it('should send changes if api success', () => {
    const store = mockStore({})

    userActions.loadSelfUser = () => {
      return dispatch => 0
    }
    api.updateProfile = async () => {
      return 'success'
    }

    store.dispatch(saveChanges({}))
      .then(() => {
        expect(store.getActions()).toEqual([])
      })
  })

  it('should modify inboxLimit if provided', () => {
    const store = mockStore({})

    api.updateProfile = async () => {
      return 'success'
    }

    return store.dispatch(saveChanges({ inboxSizeChanged: true, inboxSize: 10 }))
      .then(() => {
        expect(store.getActions()).toEqual([])
      })
  })
})

describe('ACTIONS startUploadingUserImage', () => {
  it('should modify store with action', () => {
    const store = mockStore({})

    return store.dispatch(startUploadingUserImage())
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

    return store.dispatch(uploadUserImage({ image: '1232234.png' }))
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

    return store.dispatch(uploadUserImage({ image: '123123.png' }, { x: 1, y: 1, width: 10, height: 10 }))
      .then(() => {
        expect(store.getActions()).toEqual([
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.DURING } },
          { type: UPDATE_DATA, payload: { avatar: '123123.png' } },
          { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.BEFORE } } ])
      })
  })
})
