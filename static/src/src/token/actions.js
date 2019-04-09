import { toAction } from 'src/common/utils'
import api from 'src/api'
import {
  GET_BALANCE_SUCCESS,
  GET_WALLET_ADDRESS_SUCCESS,
  LIST_TRANSACTIONS_IN_SUCCESS,
  LIST_TRANSACTIONS_OUT_SUCCESS,
  TOKEN_ERROR,
  WITHDRAW_SUCCESS
} from './action-types'

export function getBalance () {
  return async dispatch => {
    try {
      const resp = await api.getBalance()
      const result = resp.data.data

      dispatch(toAction(GET_BALANCE_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}

export function listTransactionsIn () {
  return async dispatch => {
    try {
      const resp = await api.fetchTransactionsIn()
      const result = resp.data.data.items

      dispatch(toAction(LIST_TRANSACTIONS_IN_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}

export function listTransactionsOut () {
  return async dispatch => {
    try {
      const resp = await api.fetchTransactionsOut()
      const result = resp.data.data.items

      dispatch(toAction(LIST_TRANSACTIONS_OUT_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}

export function qtumNetworkSync () {

  return async dispatch => {
    try {
      const resp = await api.networkSync()
      const result = resp.data.data

      // TODO perhaps using the same GET_BALANCE_SUCCESS may lead to future bugs
      dispatch(toAction(GET_BALANCE_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}

export function getInWalletAddress () {

  return async dispatch => {
    try {
      const resp = await api.getInAddress()
      const result = resp.data.data

      dispatch(toAction(GET_WALLET_ADDRESS_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}

export function withdraw (destinationAddress, amount) {
  return async dispatch => {
    try {
      // Were using 8 decimal places to work with QTUM standard
      const amountToFloat = parseFloat(amount).toFixed(8)
      const resp = await api.withdraw({
          'destination_address': destinationAddress,
          'amount': amountToFloat
        })
      const result = resp.data.data

      dispatch(toAction(WITHDRAW_SUCCESS, result))
    } catch (error) {
      dispatch(toAction(TOKEN_ERROR, error))
    }
  }
}


