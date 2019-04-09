import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { injectIntl, FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { updateUserInboxSize } from 'src/user/actions'
import { LunaAgeSlider, LunaSubmit } from 'src/views/components'

class SettingsStep extends Component {

  constructor (props) {
    super(props)
    this.state = {
      seekingAgeFrom: this.props.user.seekingAgeFrom || 18,
      seekingAgeTo: this.props.user.seekingAgeTo || 45,
      inboxSize: this.props.user.inboxSize
    }
  }

  handleAgeChange = (event) => {
    this.setState({
      seekingAgeFrom: event[ 0 ],
      seekingAgeTo: event[ 1 ],
    })
  }

  handleInboxSizeChange = (event) => {
    this.setState({
      inboxSize: event,
      inboxSizeChanged: true,
    })
  }

  renderAgeSlider () {
    return <LunaAgeSlider
      values={ [ this.state.seekingAgeFrom, this.state.seekingAgeTo ] }
      onChange={ this.handleAgeChange }/>
  }

  render () {
    const { seekingAgeFrom, seekingAgeTo } = this.state
    return (
      <div className='step'>
        <h1 className='title'><FormattedMessage id={'fill.setting.header'}/></h1>
        <form onSubmit={ (event) => this.handleSubmit(event) } noValidate>
          <div className='label-container'>
            <span className='description'><FormattedMessage id={'fill.setting.age_prompt'}/></span>
            <div className='age-container'>
              <span>{ seekingAgeFrom }</span>-
              <span>{ seekingAgeTo }</span>
            </div>
          </div>
          <div>
            { this.renderAgeSlider() }
          </div>
          <div className='label-container'>
            <span className='description'><FormattedMessage id={'fill.setting.inbox_limit'}/></span>
            <div className='inboxSize-container'>
              <span>
                { `max 10 intros/day` }</span>
            </div>
          </div>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderSubmit () {
    return <LunaSubmit/>
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()
    const { seekingAgeFrom, seekingAgeTo, inboxSize, inboxSizeChanged } = this.state

    this.props.onUpdate({
      seekingAgeFrom,
      seekingAgeTo,
      inboxSize,
      inboxSizeChanged
    })
  }
}

SettingsStep.propTypes = {
  onUpdate: PropTypes.func.isRequired
}

const mapDispatchToProps = {
  updateUserInboxSize
}

export default injectIntl(connect(null, mapDispatchToProps)(SettingsStep))
