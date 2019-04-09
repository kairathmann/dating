import { List, Record } from 'immutable'
import { toast } from 'react-toastify'
import { SIGN_OUT_SUCCESS } from 'src/auth/action-types'
import { getErrorMessage } from 'src/common/utils'

import {
  CHANGE_RECOMMENDATIONS_INDEX,
  GET_CAN_MATCH_ERROR,
  INCREMENT_RECOMMENDATIONS_INDEX,
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

export const RecommendationsState = new Record({
  list: new List(),
  biddingUser: null,
  lastReactionConversationId: null,
  index: 0,
  isLoadingRecommendations: false,
  targetUser: null, // @view property by setTargetUser reducer-middleware,
  isShowingSkipped: false
})

function recommendationsReducer (state = new RecommendationsState(), { payload, type }) {
  switch (type) {
    case LOAD_RECOMMENDATIONS_SUCCESS:
      return state.set('list', new List(payload.people))

    case SET_BIDDING_USER:
      return state.set('biddingUser', payload)

    case SET_REACTION_SUCCESS:
      return state.set('lastReactionConversationId', payload.data.conversationId)

    case SIGN_OUT_SUCCESS:
      return new RecommendationsState()

    case LOAD_RECOMMENDATIONS_PROGRESS:
      return state.set('isLoadingRecommendations', payload)

    case CHANGE_RECOMMENDATIONS_INDEX:
      return state.set('index', payload)

    case INCREMENT_RECOMMENDATIONS_INDEX:
      return state.set('index', state.index + 1)

    case SET_CONVERSATIONS_SUCCESS:
      toast.success('Message sent!')
      return state

    case SET_REACTION_ERROR:
    case GET_CAN_MATCH_ERROR:
    case SET_CONVERSATIONS_ERROR:
      toast.error(getErrorMessage(payload.response))
      return

    case SET_NEXT_TARGET_USER:
      const listElement = state.get('list').get(0)
      if(listElement) {
        return state.set('targetUser', {
          ...listElement, photoURL: listElement.avatarUrl, state: 2
        })
      }
      else return state.set('targetUser', null)

    case REMOVE_USER_FROM_LIST:
      const newList = state.get('list').delete(0)
      return state.set('list', newList)

    case SHOW_SKIPPED:
      return state.set('isShowingSkipped', true)

    default:
      return state
  }
}
export default recommendationsReducer

