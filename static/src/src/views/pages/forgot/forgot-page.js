import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'
import { getErrorMessage } from 'src/common/utils'
import { BackButton } from 'src/views/components'

import './forgot-page.css'

export class ForgotPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      email: '',
    }
  }

  render () {
    const lastResult = getErrorMessage(this.props.auth.forgotPasswordLastResult)
    return (
      <div className='forgot-page'>
        <BackButton
          onBack={ this.props.clearLastError }
          history={ this.props.history }/>
        <h1 className='title'><FormattedMessage id={ 'forgot.header' }/></h1>
        <div className='errors'>{ lastResult }</div>
        <form onSubmit={ this.handleSubmit } noValidate>
          <div className='input-group'>
            <label className='label' htmlFor='email'><FormattedMessage id={ 'common.email' }/></label>
            { this.renderInput('email', '', 'email') }
          </div>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderInput (fieldName, placeholder, inputType = 'text') {
    return (<input
      className='input'
      type={ inputType }
      name={ fieldName }
      value={ this.state[ fieldName ] }
      placeholder={ placeholder }
      ref={ e => this[ fieldName + 'Input' ] = e }
      onChange={ this.handleChange }
    />)
  }

  renderSubmit () {
    const { intl } = this.props
    return (
      <input className='button submit-btn' type='submit'
             value={ intl.formatMessage({ id: 'forgot.reset_password' }) }/>)
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()
    this.props.clearLastError()
    this.props.forgotPassword({ email: this.state.email })
  }
}

ForgotPage.propTypes = {
  forgotPassword: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  forgotPassword: authActions.forgotPassword,
  clearLastError: authActions.clearLastError
}

export default injectIntl(
  withRouter(
    connect(
      mapStateToProps,
      mapDispatchToProps
    )(ForgotPage)))
