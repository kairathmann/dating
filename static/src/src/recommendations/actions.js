import { toAction } from 'src/common/utils'
import routes, { toPath } from 'src/routes'
import api from 'src/api'
import { avatarUrlToPhotoUrlObj, rewriteUrlImageForDefault } from '../common/utils'

import {
  CHANGE_RECOMMENDATIONS_INDEX,
  GET_CAN_MATCH_ERROR,
  INCREMENT_RECOMMENDATIONS_INDEX,
  LOAD_RECOMMENDATIONS_ERROR,
  LOAD_RECOMMENDATIONS_PROGRESS,
  LOAD_RECOMMENDATIONS_SUCCESS,
  SET_BIDDING_USER,
  SET_CONVERSATIONS_ERROR,
  SET_CONVERSATIONS_SUCCESS,
  SET_REACTION_ERROR,
  SET_REACTION_SUCCESS,
  SET_NEXT_TARGET_USER,
  SHOW_SKIPPED,
  REMOVE_USER_FROM_LIST
} from './action-types'

export function loadRecommendations (showLoader = true) {
  return dispatch => {
    if(showLoader) {
      dispatch(toAction(LOAD_RECOMMENDATIONS_PROGRESS, true))
    }
    return api.fetchRecommendations()
      .then(({ data }) => processProfiles(data, dispatch))
      .catch(error => handleFetchProfilesError(error, dispatch))
  }
}

export function loadSkipped(showLoader = true) {
  return dispatch => {
    dispatch(toAction(SHOW_SKIPPED))
    if(showLoader) {
      dispatch(toAction(LOAD_RECOMMENDATIONS_PROGRESS, true))
    }
    return api.fetchSkipped()
      .then(({ data }) => processProfiles(data, dispatch))
      .catch(error => handleFetchProfilesError(error, dispatch))
  }
}

function handleFetchProfilesError (error, dispatch) {
  dispatch(toAction(LOAD_RECOMMENDATIONS_ERROR, error))
  return dispatch(toAction(LOAD_RECOMMENDATIONS_PROGRESS, false))
}

function processProfiles ( data, dispatch) {
  const respData = data.data
  const people = respData.people.map(person => {
    const { avatarUrl, gidIs: gender } = person
    let { photoURL: avatar } = avatarUrlToPhotoUrlObj(avatarUrl)
    avatar = rewriteUrlImageForDefault(avatar, gender)

    const tempImg = new Image()
    tempImg.src = avatar

    return {
      ...person,
      avatarUrl: avatar
    }
  })
  dispatch(toAction(LOAD_RECOMMENDATIONS_SUCCESS, { ...respData, people }))
  dispatch(toAction(SET_NEXT_TARGET_USER))
  dispatch(toAction(LOAD_RECOMMENDATIONS_PROGRESS, false))
  return
}

export function handleReaction (targetUser, isMatch, history) {
  return async (dispatch, getState) => {
    if (isMatch) {
      await dispatch(getCanMatch(
        targetUser,
        () => {history.push(toPath(routes.bid))},
        () => {history.push(toPath(routes.newMessage, targetUser.hid))}
      ))
    } else {
      await dispatch(
        setUnmatch(
          targetUser.hid,
          () => {history.push(toPath(routes.recommendations))}
        )
      )
    }
    await dispatch(toAction(REMOVE_USER_FROM_LIST))
    if( getState().recommendations.get('list').size === 0) {
      if(!getState().recommendations.get('isShowingSkipped')){
        await dispatch(loadRecommendations(false))
      } else {
        await dispatch(loadSkipped(false))
      }
    }
    dispatch(toAction(SET_NEXT_TARGET_USER))
  }
}

export function getCanMatch (targetUser, redirectToBidding, redirectToMessage) {
  return async dispatch => {
    try {
      // todo: check that place
      if (parseFloat(targetUser.minBid) === 0) {
        redirectToMessage()
      } else {
        redirectToBidding()
        dispatch(toAction(SET_BIDDING_USER, targetUser))
      }
    } catch (error) {
      dispatch(toAction(GET_CAN_MATCH_ERROR, error))
    }
  }
}

export function createConversation (reaction, redirect) {
  return async dispatch => {
    try {
      const response = await api.createConversation(reaction)
      dispatch(toAction(SET_CONVERSATIONS_SUCCESS, response))

      if (redirect) {
        setTimeout(() => {
          redirect()
        }, 0)
      }
      return
    } catch (error) {
      dispatch(toAction(SET_CONVERSATIONS_ERROR, error))
    }
  }
}

export function setUnmatch (targetUserId) {
  return async dispatch => {
    try {
      const response = await api.unmatch({ 'recipient_hid': targetUserId })
      dispatch(incrementRecommendations())
      dispatch(toAction(SET_REACTION_SUCCESS, response.data))
      return dispatch(toAction(SET_REACTION_SUCCESS, response.data))
    } catch (error) {
      dispatch(toAction(SET_REACTION_ERROR, error))
    }
  }
}

export function resetRecommendationsIndex () {
  return {
    type: CHANGE_RECOMMENDATIONS_INDEX,
    payload: 0,
  }
}

export function incrementRecommendations () {
  // TODO There is a more pragmatic way to do that that receive the old recommendIndex
  // yonatan - I guess we can remove reacted recommendations from list head and always be on index 0
  return {
    type: INCREMENT_RECOMMENDATIONS_INDEX,
  }
}
