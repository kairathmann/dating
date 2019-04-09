import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import Select from 'react-select'
import { GENDER } from 'src/enums'
import { LunaSubmit } from 'src/views/components'

class GenderStep extends Component {
  constructor (props) {
    super(props)
    this.state = {
      gender: this.props.user.gidIs,
      sexuality: this.props.user.gidSeeking
    }
  }

  genderDefaults = [
    { value: GENDER.MALE, label: this.props.intl.formatMessage({id: 'common.man'})},
    { value: GENDER.FEMALE, label: this.props.intl.formatMessage({id: 'common.woman'})},
    { value: GENDER.OTHER, label: this.props.intl.formatMessage({id: 'common.other'}) }
  ]

  sexualityDefaults = [
    { value: GENDER.MALE, label: this.props.intl.formatMessage({id: 'common.men'}) },
    { value: GENDER.FEMALE, label: this.props.intl.formatMessage({id: 'common.women'}) },
    { value: GENDER.BOTH, label: this.props.intl.formatMessage({id: 'common.both'}) }
  ]

  render () {
    const { intl } = this.props
    return (
      <div className='step'>
        <h1 className='title'><FormattedMessage id={'fill.gender.header'}/></h1>
        <form onSubmit={ (event) => this.handleSubmit(event) } noValidate>
          { this.renderSelect(intl.formatMessage({id: 'fill.gender.gender_prompt'}), 'gender', intl.formatMessage({id: 'common.choose'}), this.genderDefaults) }
          { this.renderSelect(intl.formatMessage({id: 'fill.gender.sexuality_prompt'}), 'sexuality', intl.formatMessage({id: 'common.choose'}), this.sexualityDefaults) }
          <p className='center'><FormattedMessage id={'fill.gender.luna'}/></p>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderSelect (title, fieldName, placeholder, options) {
    return (
      <div className='input-group'>
        <Select
          type='text'
          name={ fieldName }
          value={ this.state[ fieldName ] }
          placeholder={ title }
          ref={ e => this[ fieldName + 'Input' ] = e }
          onChange={ (e) => {
            let val = null
            if (e) {
              val = e.value
            }
            this.setState({ [ fieldName ]: val })
          } }
          options={ options }
          noResultsText={ 'Nothing found' }
          searchable={ false }
          clearable={ false }
        />
      </div>
    )
  }

  renderSubmit () {
    const { gender, sexuality } = this.state
    return <LunaSubmit disabled={ (gender === null || sexuality === null) }/>
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()
    this.props.onUpdate({
      gidIs: this.state.gender,
      gidSeeking: this.state.sexuality
    })
  }
}

GenderStep.propTypes = {
  onUpdate: PropTypes.func.isRequired
}

export default injectIntl(GenderStep)
