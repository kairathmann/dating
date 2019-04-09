import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import { todayXyearsAgoAsStr, getAge } from 'src/common/utils'
import { LunaInput, LunaSubmit } from 'src/views/components'

class AboutStep extends Component {
  constructor (props) {
    super(props)
    this.state = {
      firstName: this.props.user.firstName,
      birthDate: this.props.user.birthDate
    }
  }

  componentWillReceiveProps (nextProps) {
    this.updateStateByProps(nextProps)
  }

  updateStateByProps (props) {
    const { user } = props
    this.setState({
      birthDate: user.birthday || '',
      firstName: user.firstName || '',
    })
  }

  render () {
    const { intl } = this.props
    return (
      <div className='step'>
        <h1 className='title'><FormattedMessage id={ 'fill.about.header' }/></h1>
        <form onSubmit={ this.handleSubmit } noValidate>
          { this.renderInput('firstName', intl.formatMessage({ id: 'fill.about.nickname' })) }
          { this.renderBirthDayInput() }
          {
            this.state.ageError && (
              <p className='red'>You are under 18 years old. You cannot use Luna.</p>
            )
          }
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderBirthDayInput () {
    const bdFieldName = 'birthDate'
    return (
      <div className="input-group">
        <input
          className='input'
          type='date'
          name={ bdFieldName }
          value={ this.state[ bdFieldName ] }
          placeholder='Birthday'
          ref={ e => this[ bdFieldName + 'Input' ] = e }
          min={ todayXyearsAgoAsStr(90) }
          max={ todayXyearsAgoAsStr(18) }
          onChange={ this.handleChange }
        />
      </div>
    )
  }

  renderInput (fieldName, placeholder) {
    return <LunaInput
      fieldName={ fieldName }
      placeholder={ placeholder }
      value={ this.state[ fieldName ] }
      onChange={ this.handleChange }
    />
  }

  renderSubmit () {
    const { firstName, birthDate } = this.state

    return <LunaSubmit disabled={ !(firstName && birthDate && getAge(birthDate) >= 18) }/>
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    const birthDate = fieldName === 'birthDate' ? e.target.value : this.state.birthDate
    this.setState({
      [ fieldName ]: e.target.value,
      ageError: getAge(birthDate) < 18
    })
  }


  handleSubmit = (event) => {
    const { birthDate } = this.state
    event && event.preventDefault()
    this.props.onUpdate({
      firstName: this.state.firstName,
      birthDate,
      seekingAgeFrom: 18,
      seekingAgeTo: 45
    })
  }
}

AboutStep.propTypes = {
  onUpdate: PropTypes.func.isRequired
}

export default injectIntl(AboutStep)
