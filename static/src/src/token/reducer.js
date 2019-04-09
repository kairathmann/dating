import { List, Record } from 'immutable'
import { toast } from 'react-toastify'
import { getErrorMessage } from 'src/common/utils'
import {
  GET_BALANCE_SUCCESS,
  GET_WALLET_ADDRESS_SUCCESS,
  LIST_TRANSACTIONS_IN_SUCCESS,
  LIST_TRANSACTIONS_OUT_SUCCESS,
  TOKEN_ERROR,
  WITHDRAW_SUCCESS
} from './action-types'

export const Token = new Record({
  confirmedBalance: null,
  unconfirmedBalance: null,
  walletAddress: null,
  transactionsIn: new List(),
  transactionsOut: new List(),
  lastWithdrawResult: null,
})

export default function conversationsReducer (state = new Token(), { payload, type }) {
  switch (type) {
    case GET_BALANCE_SUCCESS:
      return state.merge({
        confirmedBalance: payload ? parseFloat(payload.confirmed) : null,
        unconfirmedBalance: payload ? parseFloat(payload.unconfirmed) : null,
      })

    case LIST_TRANSACTIONS_IN_SUCCESS:
      return state.merge({
        transactionsIn: new List(payload.reverse()),
      })

    case LIST_TRANSACTIONS_OUT_SUCCESS:
      return state.merge({
        transactionsOut: new List(payload.reverse()),
      })

    case GET_WALLET_ADDRESS_SUCCESS:
      return state.merge({
        walletAddress: payload ? payload.qtumAddress : null,
      })

    case WITHDRAW_SUCCESS:

      // TODO: INTL
      toast.success(`Successfully withdraw ${payload.amount}. Txid:${payload.txid}`)
      return state.merge({
        lastWithdrawResult: payload
      })

    case TOKEN_ERROR:
      toast.error(getErrorMessage(payload.response))
      return state

    default:
      return state
  }
}
