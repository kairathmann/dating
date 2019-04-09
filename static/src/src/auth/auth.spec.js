/* eslint no-throw-literal: 0 */
import * as actions from 'src/user/actions'
import { initAuth } from './auth'

describe('AUTH initAuth', () => {
  it('should call resolve if success', async () => {
    actions.loadSelfUser = () => {
      return async (dispatch) => {
        return 'success'
      }
    }

    initAuth({})
      .then(res => {
        expect(res).toEqual(undefined)
      })
  })

  it('should fail', async () => {
    actions.loadSelfUser = () => {
      return async (dispatch) => {
        throw 'error'
      }
    }

    initAuth({})
      .catch(err => {
        expect(err).toEqual('error')
      })
  })
})
