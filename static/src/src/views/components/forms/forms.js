import classNames from 'classnames'
import Slider from 'rc-slider'
import React from 'react'
import { injectIntl } from 'react-intl'
import Textarea from 'react-textarea-autosize'
import { CONSTANTS } from 'src/enums'

const Range = Slider.createSliderWithTooltip(Slider.Range)

export function LunaAgeSlider (props) {
  const { values, onChange } = props
  return <Range min={ CONSTANTS.MIN_AGE } max={ CONSTANTS.MAX_AGE }
                pushable={ true }
                className='luna-slider'
                value={ values }
                handleStyle={ [ {
                  width: '3rem',
                  height: '3rem',
                  marginTop: '-1.2rem'
                } ] }
                tipFormatter={ value => value }
                onChange={ onChange }/>
}

export function LunaTextArea (props) {
  const { fieldName, value, placeholder, onChange, size = 50, showCounter = true } = props
  return (
    <div>
    <Textarea
      className={ classNames('textarea', fieldName) }
      name={ fieldName }
      value={ value }
      placeholder={ placeholder }
      maxLength={ size }
      onChange={ onChange }/>
      { showCounter &&
      <p className='text-area-counter'>{ value.length }/{ size }</p>
      }

    </div>)
}

export function LunaInput (props) {
  const { inputType = 'text', fieldName, placeholder, onChange, value } = props
  return (
    <div className="input-group">
      <input
        className='input'
        type={ inputType }
        name={ fieldName }
        value={ value }
        placeholder={ placeholder }
        onChange={ onChange }
      />
    </div>
  )
}

function LunaSubmitFnc (props) {
  const { intl } = props
  const { disabled = false, value = intl.formatMessage({id: 'common.next'})} = props
  const classes = {
    'button submit-btn': true,
    'disabled': disabled
  }
  return <input disabled={ disabled } className={ classNames(classes) } type='submit' value={ value }/>
}

export const LunaSubmit = injectIntl(LunaSubmitFnc)

