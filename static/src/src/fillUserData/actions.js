import api from 'src/api'
import { toAction } from 'src/common/utils'
import { ASYNC_STATES } from 'src/enums'
import { loadSelfUser, updateUserInboxSize } from 'src/user/actions'
import { START_FILL_DATA, UPDATE_DATA, UPLOAD_USER_IMAGE_DONE } from './action-types'

export function updateUser (changes) {
  return dispatch => {
    return dispatch(toAction(UPDATE_DATA, changes))
  }
}

export function startFillData () {
  return dispatch => {
    return dispatch(toAction(START_FILL_DATA, {}))
  }
}

export function saveChanges (changes) {
  return async dispatch => {
      if (changes.inboxSizeChanged) {
        dispatch(updateUserInboxSize(parseInt(changes.inboxSize, 10)))
      }
      await api.updateProfile(changes)
      return loadSelfUser()(dispatch)
  }
}

function uploadUserStatusActionCreator (status) {
  return toAction(UPLOAD_USER_IMAGE_DONE, { status })
}

export function startUploadingUserImage () {
  return async dispatch => {
    dispatch(uploadUserStatusActionCreator(ASYNC_STATES.DURING))
  }
}

export function uploadUserImage (imageFile) {

  const data = new FormData()
  const maxSize = 1000

  data.append('resize_width', `${maxSize}`)
  data.append('resize_height', `${maxSize}`)
  data.append('image', imageFile)

  return async dispatch => {
    dispatch(uploadUserStatusActionCreator(ASYNC_STATES.DURING))
    try {
      const { data: uploadRespData } = await api.uploadAvatar(data)
      const { avatarUrl } = uploadRespData
      dispatch(updateUser({ avatar: avatarUrl }))

      dispatch(uploadUserStatusActionCreator(ASYNC_STATES.BEFORE)) // no need for success stage
      return
    } catch (e) {
      dispatch(uploadUserStatusActionCreator(ASYNC_STATES.FAIL))
    }
  }
}

