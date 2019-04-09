import { toAction } from 'src/common/utils'
import { ASYNC_STATES } from 'src/enums'

import { loadSelfUser } from 'src/user/actions'
import api from 'src/api'
import {
  LOAD_EDIT_DATA_FOR_USER_ERROR,
  LOAD_EDIT_DATA_FOR_USER_START,
  LOAD_EDIT_DATA_FOR_USER_SUCCESS,
  UPLOAD_USER_IMAGE_DONE
} from './action-types'

export function loadEditDataForUser () {
  return async dispatch => {
    try {
      dispatch(toAction(LOAD_EDIT_DATA_FOR_USER_START))
      const response = await api.loadUserForEdit()
      dispatch(toAction(LOAD_EDIT_DATA_FOR_USER_SUCCESS, response.data.data))
      loadSelfUser()(dispatch)
      return
    } catch (error) {
      dispatch(toAction(LOAD_EDIT_DATA_FOR_USER_ERROR, error))
    }
  }
}

/**
 *
 * @param status: {ASYNC_STATES}
 */
function uploadUserStatusActionCreator (status) {
  return toAction(UPLOAD_USER_IMAGE_DONE, { status })
}

export function startUploadingUserImage () {
  return async dispatch => {
    dispatch(uploadUserStatusActionCreator(ASYNC_STATES.DURING))
  }
}

export function uploadUserImage (imageFile, cropOptions) {

  const data = new FormData()
  const maxSize = 1000

  data.append('resize_width', `${maxSize}`)
  data.append('resize_height', `${maxSize}`)
  data.append('image', imageFile)

  return async dispatch => {
    dispatch(uploadUserStatusActionCreator(ASYNC_STATES.DURING))
    try {
      const { data: uploadRespData } = await api.uploadAvatar(data)

      const { viewerHid } = uploadRespData

      await loadEditDataForUser(viewerHid)(dispatch)
      dispatch(uploadUserStatusActionCreator(ASYNC_STATES.BEFORE)) // no need for success stage
      return
    } catch (e) {
      dispatch(uploadUserStatusActionCreator(ASYNC_STATES.FAIL))
    }
  }
}


