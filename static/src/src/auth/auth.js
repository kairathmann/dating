import { loadSelfUser } from 'src/user/actions'

export function initAuth (dispatch) {
  return new Promise((resolve, reject) => {
    loadSelfUser()(dispatch)
      .then(() => {
        resolve()
      })
      .catch(err => {
        reject(err)
      })
  })
}
