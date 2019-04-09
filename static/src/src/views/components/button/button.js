import classNames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import './button.css'

const Button = ({ children, className, onClick, disabled }) => {
  const cssClasses = classNames('button', className)
  return (
    <button className={ cssClasses } disabled={ disabled } onClick={ onClick } type='button'>
      { children }
    </button>
  )
}

Button.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  onClick: PropTypes.func,
}

export default Button
