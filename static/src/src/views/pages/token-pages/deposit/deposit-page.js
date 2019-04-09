import Clipboard from 'clipboard'
import PropTypes from 'prop-types'
import QRCode from 'qrcode.react'
import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { getDateStrs } from 'src/common/utils'
import routes, { toPath } from 'src/routes'
import { tokenActions } from 'src/token/index'
import { userActions } from 'src/user/index'

import TokenHeader from '../token-pages-header'
import './deposit-page.css'

class DepositPage extends Component {
  constructor () {
    super(...arguments)

    this.state = {
      confirmedBalance: '',
      unconfirmedBalance: '',
      transactions: []
    }
  }

  componentWillMount () {
    this.props.getBalance()
    this.props.listTransactionsIn()
    this.props.getInWalletAddress()
    this.props.qtumNetworkSync()
    this.updateStateByProps(this.props)
  }

  componentWillReceiveProps (nextProps) {
    this.updateStateByProps(nextProps)
  }

  updateStateByProps (props) {
    const { token } = props

    this.setState({
      confirmedBalance: token.confirmedBalance || 0,
      unconfirmedBalance: token.unconfirmedBalance || 0,
      walletAddress: token.walletAddress || null,
    })
    this.renderQr(token.walletAddress)
  }

  componentDidMount () {
    this.renderQr(this.state.walletAddress)
    // TODO: We must call this method twice for it to work
    // So this doesn't really copy it just enable the next copy
    this.copyWalletAddress()
  }

  renderQr (walletAddress) {
    if (!walletAddress) {
      return
    }
    const qrCode = document.getElementById('qr-code')
    if (!qrCode) {
      return
    }
    ReactDOM.render(
      <QRCode
        value={ `qtum:${walletAddress}` }
        size={ 184 }
        level={ 'Q' }
        fgColor={ '#603695' }
        bgColor={ '#dbdbdb' }
      />,
      qrCode
    )
  }

  renderTransaction (transaction) {
    const {
      created,
      amount,
    } = transaction
    const createdDate = new Date(created)

    // TODO: currently we're only displaying confirmed transactions
    const status = TRANSACTION_STATUS.CONFIRMED

    const statusStr = status === TRANSACTION_STATUS.PENDING ? 'Pending' : 'Confirmed'
    const statusClassClr = status === TRANSACTION_STATUS.PENDING ? 'red' : 'green'

    const amountModifier = amount > 0 ? '+' : '-'

    const [ dayStr, timeStr ] = getDateStrs(createdDate)
    return <div className='transaction' key={ createdDate.getTime() }>
      <div className='transaction-time-and-status-container'>
        <div className='transaction-date'>
          <span className='transaction-day'>{ dayStr }</span>
          <span className='transaction-time'>{ timeStr }</span>
        </div>
        <div className={ `transaction-status ${statusClassClr}` }>{ statusStr }</div>
      </div>

      <div className='amount-container'>
        <span className='amount-sum'>{ amountModifier }{ amount }</span>
        <span className='stars'>Stars</span>
      </div>


    </div>
  }

  render () {
    const { transactions, intl } = this.props
    return (
      <div className='deposit-page'>
        <TokenHeader
          title={ intl.formatMessage({ id: 'balance.deposit' }) }
          backPath={ toPath(routes.tokenBalance) }
        />

        <div className='body'>
          <div className='deposit-container'>
            <div className='deposit-info'>
              <h1><FormattedMessage id={ 'deposit.header' }/></h1>
              <p>To learn more, including how to swap your LSTR[QTUM] for LSTR[ETH], read our <u><a href="https://medium.com/lunalabs/token-swap-instructions-84eedd79adb3">blog post</a></u>.</p>
            </div>
          </div>
          <div className='transaction-history'>
            <div className='title text bold mid-large'><FormattedMessage id={ 'deposit.transaction_history' }/></div>

            <div className='transaction-list'
                 onClick={ () => {this.props.history.push(toPath(routes.transactionHistory))} }>
              { transactions.map(this.renderTransaction) }
            </div>
          </div>
        </div>
      </div>
    )
  }

  copyWalletAddress () {
    new Clipboard('.copy-btn')
  }

}

DepositPage.propTypes = {
  getInWalletAddress: PropTypes.func.isRequired,
  qtumNetworkSync: PropTypes.func.isRequired,
  getBalance: PropTypes.func.isRequired,
  listTransactionsIn: PropTypes.func.isRequired,
  token: PropTypes.shape({
    confirmedBalance: PropTypes.number,
    unconfirmedBalance: PropTypes.number,
  }).isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
    token: state.token,
    transactions: state.token.transactionsIn.toArray(),
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  tokenActions,
)

export default injectIntl(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(DepositPage))

const TRANSACTION_STATUS = {
  PENDING: 'PENDING',
  CONFIRMED: 'CONFIRMED',
}
