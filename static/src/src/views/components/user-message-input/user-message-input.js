import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { injectIntl } from 'react-intl'
import Textarea from 'react-textarea-autosize'
import { srcByRetina } from 'src/common/utils'

import { ASYNC_STATES } from 'src/enums'
import sendIconSmall from 'src/images/send.png'
import sendIconMedium from 'src/images/send@2x.png'
import sendIconBig from 'src/images/send@3x.png'

import LunaLoader, { LOGO_COLORS } from 'src/views/components/loaders/luna-loader'

import './user-message-input.css'

export class UserMessageInput extends Component {
  constructor (props) {
    super(props)
    this.state = {
      body: '',
    }
  }

  render () {
    const { stickDown, submitButtonCenter } = this.props
    return (
      <form
        onSubmit={ this.handleSubmit }
        noValidate
        className={ classnames(
          'user-message-input',
          stickDown && 'stick-down',
          submitButtonCenter && 'submit-button-center'
        ) }
      >
        { this.renderTextArea('body', this.props.intl.formatMessage({id: 'common.write_here'})) }
        { this.renderSubmit() }
      </form>
    )
  }

  componentDidUpdate (provProps) {
    if (provProps.sendState === ASYNC_STATES.DURING && this.props.sendState === ASYNC_STATES.BEFORE) { // after success
      this.setState({ body: '' })
    }
  }

  renderTextArea (fieldName, placeholder) {
    const { onHeightChange } = this.props
    return (
      <Textarea
        className='user-message-input-textarea'
        name={ fieldName }
        value={ this.state[ fieldName ] }
        placeholder={ placeholder }
        ref={ e => this[ fieldName + 'Input' ] = e }
        onChange={ this.handleMessageChange }
        onKeyDown={ this.handleKey.bind(this) }
        onHeightChange={ onHeightChange }
      />)
  }

  handleKey = (event) => {
    if (event.keyCode === 13 && !event.shiftKey) {
      this.handleSubmit(event)
    }
  }

  renderSubmit () {
    const { sendState } = this.props
    if (sendState === ASYNC_STATES.DURING) {
      return (
        <div className="submit-button center">
          <LunaLoader logoColor={ LOGO_COLORS.PURPLE } sizeInRem={ 1 } dotSizeInRem={ 0.5 }/>
        </div>
      )
    } else if (sendState === ASYNC_STATES.FAIL) {
      return (
        <span className="submit-button text fail">
          failed
        </span>
      )

    } else { // sendState === ASYNC_STATES.BEFORE

      const { body } = this.state
      const isActive = !!body && body.length > 0

      return (
        <div className={ classnames('submit') }>
          { isActive &&
          <img alt='Send' onClick={ this.handleSubmit }
               src={ srcByRetina(sendIconSmall, sendIconMedium, sendIconBig) }/>
          }
        </div>)
    }
  }

  handleMessageChange = (e) => {
    this.setState({
      body: e.target.value,
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()
    if (
      this.props.sendState === ASYNC_STATES.BEFORE &&
      this.state.body && this.state.body.length > 0
    ) {
      this.props.onSubmit(this.state.body)
    }
  }
}

UserMessageInput.defaultProps = {
  sendState: ASYNC_STATES.BEFORE
}

UserMessageInput.propTypes = {
  onHeightChange: PropTypes.func,
  onSubmit: PropTypes.func.isRequired,
  stickDown: PropTypes.bool,
  submitButtonCenter: PropTypes.bool,
  sendState: PropTypes.oneOf(Object.values(ASYNC_STATES))
}

export default injectIntl(UserMessageInput)
