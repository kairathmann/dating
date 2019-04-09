import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { injectIntl, FormattedMessage } from 'react-intl'
import { LunaSubmit, LunaTextArea } from 'src/views/components'

class TaglineStep extends Component {
  constructor (props) {
    super(props)
    this.state = {
      tagline: this.props.user.tagline
    }
  }

  render () {
    const {intl} = this.props
    return (
      <div className='step'>
        <h1 className='title'><FormattedMessage id={'fill.tagline.header'}/></h1>
        <form onSubmit={ (event) => this.handleSubmit(event) } noValidate>
          { this.renderTextArea('tagline', intl.formatMessage({id: 'fill.tagline.placeholder'})) }
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderTextArea (fieldName, placeholder) {
    return <LunaTextArea value={ this.state[ fieldName ] } fieldName={ fieldName } placeholder={ placeholder }
                         onChange={ this.handleChange }/>
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
    this.props.onUpdate({
      tagline: this.state.tagline
    })
  }
}

TaglineStep.propTypes = {
  onUpdate: PropTypes.func.isRequired
}

export default injectIntl(TaglineStep)
