import classnames from 'classnames'
import React, { Component } from 'react'
import { FormattedHTMLMessage, FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'
import { getErrorMessage } from 'src/common/utils'
import routes, { toPath } from 'src/routes'
import { BackButton } from 'src/views/components'

import './signup-page.css'

const MIN_PASSWORD_LENGTH = 8

export class SignupPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      email: '',
      password: '',
      auth: null,
    }
  }

  render () {
    const lastResult = getErrorMessage(this.props.auth.signUpLastResult)
    const { intl } = this.props
    return (
      <div className='signup'>
        <BackButton
          onBack={ this.props.clearLastError }
          history={ this.props.history }/>
        <h1 className='title'><FormattedMessage id={ 'signup.header' }/></h1>
        <div className='errors'>{ lastResult }</div>
        <form onSubmit={ this.handleSubmit } noValidate>
          { this.renderInput('email', intl.formatMessage({ id: 'common.email' }), 'email') }
          { this.renderInput('password', intl.formatMessage({ id: 'signup.password_placeholder' }), 'password') }
          <p className='terms'>
            <FormattedHTMLMessage id={ 'signup.policy' }/>
          </p>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderInput (fieldName, placeholder, inputType = 'text') {
    return (
      <div className="input-group">
        <input
          className='input'
          type={ inputType }
          name={ fieldName }
          autoComplete='new-password'
          value={ this.state[ fieldName ] }
          placeholder={ placeholder }
          ref={ e => this[ fieldName + 'Input' ] = e }
          onChange={ this.handleChange }
        />
      </div>
    )
  }

  renderSubmit () {
    const { intl } = this.props
    const { email, password } = this.state
    const correct = !!(email && password) && password.length >= MIN_PASSWORD_LENGTH
    const classes = {
      'button submit-btn': true,
      'disabled': !correct
    }
    return (
      <input disabled={ !correct } className={ classnames(classes) } type='submit'
             value={ intl.formatMessage({ id: 'common.next' }) }/>)
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
    this.props.signUp({
      'email': this.state.email,
      'password': this.state.password
    }, () => {
      this.props.history.push(toPath(routes.fill))
    })
  }
}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  signUp: authActions.signUp,
  clearLastError: authActions.clearLastError
}

export default injectIntl(
  withRouter(
    connect(
      mapStateToProps,
      mapDispatchToProps
    )(SignupPage)))
