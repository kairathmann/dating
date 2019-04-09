import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'
import { getErrorMessage } from 'src/common/utils'
import routes, { token, toPath } from 'src/routes'
import { BackButton } from 'src/views/components'

import './reset-pass.css'

export class ResetPassPage extends Component {
  constructor (props) {
    super(props)
    this.state = {
      password: '',
    }
  }

  render () {
    const lastResult = getErrorMessage(this.props.auth.resetPasswordLastResult)

    return (
      <div className='reset-pass-page'>
        <BackButton
          onBack={ this.props.clearLastError }
          history={ this.props.history }/>
        <h2 className='title'><FormattedMessage id={ 'reset.header' }/></h2>
        <div className='errors'>{ lastResult }</div>
        <form onSubmit={ this.handleSubmit } noValidate>
          <div className='input-group'>
            <label className='label' htmlFor='password'><FormattedMessage id={ 'common.password' }/></label>
            { this.renderPwdInput() }
          </div>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderPwdInput () {
    return (<input
      name='password'
      className='input'
      type='password'
      value={ this.state.password }
      onChange={ this.handleChange }
    />)
  }

  renderSubmit () {
    const {intl} = this.props
    return (
      <input className='button submit-btn' type='submit' value={ intl.formatMessage({id: 'common.send'})}/>)
  }

  handleChange = (e) => {
    this.setState({
      password: e.target.value,
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()
    this.props.clearLastError()
    this.props.resetPassword(
      { password: this.state.password, token: this.props.match.params[ token ] },
      () => { this.props.history.push(toPath(routes.welcome))}
    )
  }
}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  resetPassword: authActions.resetPassword,
  clearLastError: authActions.clearLastError
}

export default injectIntl(
  withRouter(
    connect(
      mapStateToProps,
      mapDispatchToProps
    )(ResetPassPage)))
