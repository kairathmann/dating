import classNames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import './header.css'

const Header = (
  {
    children,
    className,
    absolute = false,
    equalSidesForStrictCenter = false,
    sticky = !absolute, // don't use sticky=true && absolute=true
  }) => (
  <div className={ classNames('header-wrapper', sticky && 'sticky') }>
    <header
      className={ classNames(
        'header',
        className,
        absolute && 'absolute',
        equalSidesForStrictCenter && 'equal-sides-for-strict-center',
      ) }>
      { children }
    </header>
  </div>
)

Header.propTypes = {
  sticky: PropTypes.bool, // for embeding in page (e.g - full view of a match)
  absolute: PropTypes.bool, // for embeding in page (e.g - full view of a match)
  equalSidesForStrictCenter: PropTypes.bool, // use this if header has 3 children, and the main should be in the
                                             // center, usually a title
}

export function HeaderTitle ({ title }) {
  return (
    <span className="header-title text bold">
      { title }
    </span>
  )
}

HeaderTitle.propTypes = {
  title: PropTypes.string.isRequired,
}

export function HeaderLogo () {
  return (
    <span className="header-logo">
      <img src="" alt=""/>
    </span>
  )
}

export function HeaderAction ({ title, onClick }) {
  return (
    <span className="header-action" onClick={ onClick }>
      { title }
    </span>
  )
}

HeaderAction.propTypes = {
  title: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default Header
