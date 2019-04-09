import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import Select from 'react-select'
import Button from 'src/views/components/button/button'
import { LunaInput, LunaTextArea } from 'src/views/components/forms/forms'

import './questionnaire.css'

class Questionnaire extends Component {

  constructor (props) {
    super(props)
    this.state = {
      reasons: [ false, false, false, false, false ],
      comment: '',
      password: ''
    }
  }

  handleConfirm = () => {
    const { password, comment, reasons } = this.state
    let reasonsString = ''
    reasons.forEach((r, index) => {
      if (r) reasonsString += `${index + 1};`
    })
    this.props.onConfirm({
      password, comment, reasons: reasonsString.slice(0, -1)
    })
  }

  handleInputChange = (event) => {
    const name = event.target.name
    const newArray = [ ...this.state.reasons ]
    newArray[ name - 1 ] = event.target.checked
    this.setState({
      reasons: newArray
    })
  }

  render () {
    return (
      <div className='questionnaire'>
        <LunaInput
          inputType={ 'password' }
          fieldName={ 'password' }
          value={ this.state.password }
          placeholder={ this.props.intl.formatMessage({id: 'forms.type_password'}) }
          onChange={ (event) => this.setState({ password: event.target.value }) }
        />
        { this.props.error &&
        <p className='errors'>{ this.props.error }</p>
        }
        <h3><FormattedMessage id='questionnaire.header_why'/></h3>
        <div className='reasons'>
          <label><input
            name="1"
            type="checkbox"
            checked={ this.state.reasons[ 0 ] }
            onChange={ this.handleInputChange }/><FormattedMessage id='questionnaire.met_somebody_here'/></label>
          <label><input
            name="2"
            type="checkbox"
            checked={ this.state.reasons[ 1 ] }
            onChange={ this.handleInputChange }/><FormattedMessage id='questionnaire.met_somebody_elsewhere'/></label>
          <label><input
            name="3"
            type="checkbox"
            checked={ this.state.reasons[ 2 ] }
            onChange={ this.handleInputChange }/><FormattedMessage id='questionnaire.other_app'/></label>
          <label><input
            name="4"
            type="checkbox"
            checked={ this.state.reasons[ 3 ] }
            onChange={ this.handleInputChange }/><FormattedMessage id='questionnaire.no_people'/></label>
          <label><input
            name="5"
            type="checkbox"
            checked={ this.state.reasons[ 4 ] }
            onChange={ this.handleInputChange }/><FormattedMessage id='questionnaire.no_matches'/></label>
        </div>
        <LunaTextArea
          fieldName={ 'comment' }
          value={ this.state.comment }
          placeholder={ this.props.intl.formatMessage({id: 'forms.put_comment'}) }
          onChange={ (event) => this.setState({ comment: event.target.value }) }
          size={ 500 }
        />
        <Button
          disabled={ !this.state.password }
          className="manage-button filled-button"
          onClick={ this.handleConfirm }>
          { this.props.confirmText }
        </Button>
      </div>
    )
  }

  renderSelect = (title, fieldName, placeholder, options) => {
    return (

      <Select
        value={ this.state.reasons }
        onChange={ e => {
          this.setState({ reasons: e })
        } }
        multi={ true }
        simpleValue={ true }
        joinValues={ true }
        options={ options }
      />
    )
  }
}

export default injectIntl(Questionnaire)
