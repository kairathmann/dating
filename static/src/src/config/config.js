import axios from 'axios/index'
import { camelizeKeys } from 'humps'

export const config = {
  baseHost: process.env.REACT_APP_BASE_HOST
}

export default () => {
  axios.defaults.baseURL = process.env.REACT_APP_AXIOS_BASE_URL
  // Needs to be set in order for cookies to be sent to the server after auth
  axios.defaults.withCredentials = process.env.REACT_APP_AXIOS_WITH_CREDENTIALS
  axios.defaults.transformResponse = [
    ...axios.defaults.transformResponse,
    data => camelizeKeys(data)
  ]
}
