import classNames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import './icon.css'

const Icon = ({ className, name }) => {
  const cssClasses = classNames('luna-icon material-icons', className)
  return <i className={ cssClasses }>{ name }</i>
}

Icon.propTypes = {
  className: PropTypes.string,
  name: PropTypes.string.isRequired,
}

export default Icon
