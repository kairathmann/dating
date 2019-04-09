import PropTypes from 'prop-types'
import React from 'react'
import { srcByRetina } from 'src/common/utils'
import logos from 'src/images/logo'

import './luna-logo.css'

export const TYPES = {
  logo: 'logo',
  icon: 'icon',
}
export const LOGOS = {
  bw_trimmed: 'bw_trimmed',
  color_trimmed: 'color_trimmed',
  wb_trimmed: 'wb_trimmed',
}
export const ICONS = {
  bw_trimmed: 'bw_trimmed',
  color_trimmed: 'color_trimmed',
  wb_trimmed: 'wb_trimmed',
  invcolor_circle: 'invcolor_circle',
  wb_circle: 'wb_circle',
}

const req = logos

const assets = {
  logo: {},
  icon: {},
}

Object.keys(req).forEach(function (path) {
  const type = path.slice(2, 6)
  const nameAndSize = path
    .slice(7) // remove "./icon_" or "./logo_"
    .slice(0, -4) // remove ".png"

  const split = nameAndSize.split('_')
  const size = parseInt(split.pop(), 10)
  const name = split.join('_')

  if (
    (type === 'logo' && !LOGOS[ name ])
    ||
    (type === 'icon' && !ICONS[ name ])
  ) {
    throw new Error(`asset ${nameAndSize} in ./images/logo is not defined in luna-logo.js`)
  }

  if (!assets[ type ][ name ]) {
    assets[ type ][ name ] = []
  }

  assets[ type ][ name ].push({ size, url: req[path] })
})

export default function Loader ({ type, name, ...rest }) {
  if (!assets[ type ][ name ]) {
    throw new Error(`requested ${type}: ${name}, doesn't exist`)
  }

  return (
    <img
      alt={ 'luna-logo' }
      src={ srcByRetina(...assets[ type ][ name ].sort((a, b) => a.size - b.size).map(el => el.url)) }
      className="luna-logo"
      { ...rest }
    />
  )
}

Loader.propTypes = {
  type: PropTypes.oneOf(Object.keys(TYPES)).isRequired,
  name: PropTypes.string.isRequired,
}
