import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'
import { getErrorMessage } from 'src/common/utils'
import { notificationActions } from 'src/notification'
import { BackButton } from 'src/views/components'

import './login-page.css'

export class LoginPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      email: '',
      password: '',
    }
  }

  render () {
    const lastResult = getErrorMessage(this.props.auth.signInLastResult)
    return (
      <div className='login'>
        <BackButton
          onBack={ this.props.clearLastError }
          history={ this.props.history }/>
        <h1 className='title'><FormattedMessage id={ 'login.login_with_email' }/></h1>
        <div className='errors'>{ lastResult }</div>
        <form onSubmit={ this.handleSubmit } noValidate>
          <div className='input-group'>
            <label className='label' htmlFor='email'><FormattedMessage id={ 'common.email' }/></label>
            { this.renderInput('email', '', 'email') }
          </div>
          <div className='input-group'>
            <label className='label' htmlFor='password'><FormattedMessage id={ 'common.password' }/></label>
            { this.renderInput('password', '', 'password') }
          </div>
          { this.renderSubmit() }
        </form>
        <div className='forgot text small gray'>
          <NavLink to={ { pathname: '/forgot' } }><FormattedMessage id={ 'login.forgot_password' }/></NavLink><br/>
        </div>
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
      <input className='button submit-btn' type='submit' value={ intl.formatMessage({ id: 'login.login' }) }/>)
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

  handleSubmit = async (event) => {
    const { intl } = this.props
    event && event.preventDefault()
    this.props.clearLastError()
    const reactivated = await this.props.signInLocal({
      email: this.state.email,
      password: this.state.password,
    })
    if (reactivated) {
      this.props.showSuccess(intl.formatMessage({ id: 'toast.reactivated' }))
    }
  }
}

LoginPage.propTypes = {
  signInLocal: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  signInLocal: authActions.signInLocal,
  clearLastError: authActions.clearLastError,
  showSuccess: notificationActions.showSuccess
}

export default injectIntl(
  withRouter(
    connect(
      mapStateToProps,
      mapDispatchToProps
    )(LoginPage)
  ))
