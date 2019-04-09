import axios from 'axios/index'
import * as humps from 'humps'
import qs from 'qs'

export default {
  signup: payload => {
    return axios.post('/user/create/', qs.stringify(payload))
  },
  signin: payload => {
    return axios.post('/user/login/', qs.stringify(payload))
  },
  forgotPassword: payload => {
    return axios.post('/auth/forgot-pass-email/', qs.stringify(payload))
  },
  resetPassword: payload => {
    return axios.post('/auth/forgot-pass-reset/', qs.stringify(payload))
  },
  confirmEmail: payload => {
    return axios.post('/email/process/', qs.stringify(payload))
  },
  logout: () => {
    return axios.post('/user/logout/')
  },
  fetchConversations: payload => {
    return axios.post('/message/conversation/retrieve/active/', payload)
  },
  loadUserForEdit: () => {
    return axios.post('/user/retrieve/edit/')
  },
  stashAvatar: payload => {
    return axios.post('/user/avatar/stash/', payload)
      .then(({ data }) => {
        if (!data.success) throw new Error('error.stashing')
        return data
      })
  },
  cropAvatar: payload => {
    return axios.post('/user/avatar/crop/', qs.stringify(payload))
  },
  uploadAvatar: payload => {
    return axios.post('/user/avatar/upload/', payload)
      .then(({ data }) => {
        if (!data.success) throw new Error('error.stashing')
        return data
      })
  },
  updateProfile: payload => {
    return axios.post('/user/update/profile/', qs.stringify(humps.decamelizeKeys(payload)))
  },
  fetchMessages: payload => {
    return axios.post('/message/conversation/retrieve/single/', qs.stringify(payload))
  },
  sendMessage: payload => {
    return axios.post('/message/message/create/', qs.stringify(payload))
  },
  fetchRecommendations: () => {
    return axios.post('/user/retrieve/recommend/')
  },
  createConversation: payload => {
    return axios.post('/message/conversation/create/', qs.stringify(payload))
  },
  unmatch: payload => {
    return axios.post('/user/update/reaction/unmatch/', qs.stringify(payload))
  },
  getBalance: () => {
    return axios.post('/token/luna/get_balance/')
  },
  fetchTransactionsIn: () => {
    return axios.post('/token/qtum/list_trans_in/')
  },
  fetchTransactionsOut: () => {
    return axios.post('/token/qtum/list_trans_out/')
  },
  networkSync: () => {
    return axios.post('/token/qtum/network_sync/')
  },
  getInAddress: () => {
    return axios.post('/token/qtum/get_in_address/')
  },
  withdraw: payload => {
    return axios.post('/token/qtum/send_trans_out/', qs.stringify(payload))
  },
  fetchSelf: () => {
    return axios.post('/user/retrieve/self/')
  },
  manageProfileState: (state, payload) => {
    return axios.post(`/user/${state}/`, qs.stringify(payload))
  },
  loadUser: payload => {
    return axios.post('/user/retrieve/single/', qs.stringify(payload))
  },
  updateUser: payload => {
    return axios.post('/user/update/profile/', qs.stringify(payload))
  },
  updateInboxLimit: payload => {
    return axios.post('/user/update/daily_inbox_limit/', qs.stringify(payload))
  },
  fetchSkipped: () => {
    return axios.post('/user/retrieve/skipped/')
  }
}
