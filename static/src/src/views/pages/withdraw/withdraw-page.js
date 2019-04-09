import PropTypes from 'prop-types'
import Slider from 'rc-slider'

import 'rc-slider/assets/index.css'
import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { getDateStrs } from 'src/common/utils'
import routes, { toPath } from 'src/routes'
import { tokenActions } from 'src/token'
import { userActions } from 'src/user'
import { Button } from 'src/views/components'

import TokenHeader from '../token-pages/token-pages-header'

import './withdraw-page.css'

class WithdrawPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      availableBalance: '',
      amount: 0,
      destinationAddress: '',
      lastWithdrawResult: ''
    }
  }

  componentWillMount () {
    this.props.getBalance()
    this.props.listTransactionsOut()
    this.updateStateByProps(this.props)
  }

  componentDidMount () {
    this.renderAmountSlider()
  }

  componentDidUpdate () {
    this.renderAmountSlider()
  }

  componentWillReceiveProps (nextProps) {
    this.updateStateByProps(nextProps)
  }

  updateStateByProps (props) {
    const { token } = props
    this.setState({
      confirmedBalance: token.confirmedBalance || 0,
    })

    if (token.lastWithdrawResult !== this.state.lastWithdrawResult) {
      this.setState({
        lastWithdrawResult: token.lastWithdrawResult,
        amount: 0,
      })
      this.props.getBalance()
      this.props.listTransactionsOut()
    }
  }

  renderWithdrawElements () {
    const { intl } = this.props
    return [
      (
        <div key='amount-container' className='amount-container'>
          <span className='description'><FormattedMessage id={ 'withdraw.amount' }/></span>
          <div className='amount-text'>
            <span>{ this.state.amount } Stars</span>
          </div>
        </div>
      ), (
        <div key='amount-slider1'>
          <div id='amount-slider' className='luna-slider'/>
        </div>), (
        <div key='destination-wrapper' className='destination-wrapper input-group'>
          <div className='textarea-description-container'>
            <span className='description'><FormattedMessage id={ 'withdraw.destination' }/></span>
          </div>
          <div>{ this.renderInput('destinationAddress', intl.formatMessage({ id: 'withdraw.enter_qtum' })) }</div>
        </div>
      ), (
        <Button key='confirm-button' className='confirm-button filled-button'
                onClick={ this.handleWithdraw }>Confirm</Button>
      )
    ]
  }

  renderNoTokensText () {
    return (
      <div className="text bold mid-large center">
        <FormattedMessage id={ 'withdraw.empty_wallet' }/>
      </div>
    )
  }

  render () {
    const { transactions } = this.props

    const hasTokens = this.state.confirmedBalance > 0
    const hasTransactions = !!transactions.length // since transactions is jsArray - see mapStateToProps

    return (
      <div className='withdraw-page'>
        <TokenHeader
          title={ 'Withdraw' }
          backPath={ toPath(routes.tokenBalance) }
        />
        <div className='body'>
          <div className='withdraw-container'>
            { hasTokens ? this.renderWithdrawElements() : this.renderNoTokensText() }


            { hasTransactions && <div className='transaction-history'>
              <div className='title text bold mid-large'><FormattedMessage id={ 'withdraw.transaction_history' }/></div>
              <div className='transaction-list'>
                { transactions.map(this.renderTransaction) }
              </div>
            </div> }
          </div>
        </div>
      </div>
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

    const statusStr = status === TRANSACTION_STATUS.PENDING ? 'common.pending' : 'common.confirmed'
    const statusClassClr = status === TRANSACTION_STATUS.PENDING ? 'red' : 'green'

    const amountModifier = amount > 0 ? '+' : ''

    const [ dayStr, timeStr ] = getDateStrs(createdDate)
    return <div className='transaction' key={ createdDate.getTime() }>
      <div className='transaction-time-and-status-container'>
        <div className='transaction-date'>
          <span className='transaction-day'>{ dayStr }</span>
          <span className='transaction-time'>{ timeStr }</span>
        </div>
        <div className={ `transaction-status ${statusClassClr}` }><FormattedMessage id={ statusStr }/></div>
      </div>

      <div className='amount-container'>
        <span className='amount-sum'>{ amountModifier }{ amount }</span>
        <span className='stars'>Stars</span>
      </div>


    </div>
  }

  renderAmountSlider () {
    const { confirmedBalance, amount } = this.state

    if (confirmedBalance === 0) { return }
    const step = 0.001
    const max = Math.floor(confirmedBalance / step) * step  // flooring the amount to {step} points after the dot so
                                                            // there won't be overflow
    ReactDOM.render(
      <Slider
        step={ step }
        min={ 0 }
        max={ max }
        value={ amount }
        onChange={ this.handleAmountChange }
      />,
      document.getElementById('amount-slider') // why like this ?
    )
  }

  renderInput (fieldName, placeholder) {
    return (<input
      type='text'
      name={ fieldName }
      value={ this.state[ fieldName ] }
      placeholder={ placeholder }
      ref={ e => this[ fieldName + 'Input' ] = e }
      onChange={ this.handleChange }
    />)
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value, // this is an anti-pattern - plz use explicit setStating
    })
  }

  handleAmountChange = (event) => {
    this.setState({
      amount: event,
    })
  }

  handleWithdraw = () => {
    this.props.withdraw(
      this.state.destinationAddress,
      this.state.amount
    )
  }
}

WithdrawPage.propTypes = {
  getBalance: PropTypes.func.isRequired,
  listTransactionsOut: PropTypes.func.isRequired,
  withdraw: PropTypes.func.isRequired,
  token: PropTypes.shape({
    confirmedBalance: PropTypes.number,
  }).isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
    token: state.token,
    transactions: state.token.transactionsOut.toArray(),
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
  )(WithdrawPage))

const TRANSACTION_STATUS = {
  PENDING: 'PENDING',
  CONFIRMED: 'CONFIRMED',
}
