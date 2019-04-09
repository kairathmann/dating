import PropTypes from 'prop-types'
import React from 'react'
import LunaLogo, { ICONS, TYPES } from 'src/views/components/luna-logo/luna-logo'
import './luna-loader.css'

export const LOGO_COLORS = {
  PURPLE: 'purple',
  WHITE: 'white',
  BLACK: 'black',
}

export default function LunaLoader (props) {
  const {
    sizeInRem = 5,
    dotSizeInRem = 1,
    logoColor = LOGO_COLORS.WHITE,
    color = logoColor // defaults to logo color (which defaults to white)
  } = props

  const iconName = (() => {
    switch (logoColor) {
      case LOGO_COLORS.BLACK:
        return ICONS.bw_trimmed
      case LOGO_COLORS.PURPLE:
        return ICONS.color_trimmed
      case LOGO_COLORS.WHITE:
      default:
        return ICONS.wb_trimmed
    }
  })()

  const size = `${sizeInRem}rem`
  const dotSize = `${dotSizeInRem}rem`

  return (
    <div className="luna-loader" style={ {
      width: size,
      height: size,
      color,
      borderColor: color,
      padding: `${sizeInRem * 0.6}rem`
    } }>
      <div className="dot-circle">
        <div className="dot" style={ {
          backgroundColor: color,
          width: dotSize,
          height: dotSize,
        } }/>
      </div>
      <LunaLogo
        type={ TYPES.icon }
        name={ iconName }
        style={ {
          width: size,
          height: size,
          color,
        } }
      />
    </div>
  )
}

LunaLoader.propTypes = {
  // color: PropTypes.string.isRequired, //see todo up
  sizeInRem: PropTypes.number.isRequired,
  dotSizeInRem: PropTypes.number,
  // todo: we will support other LOGO_COLORS if luna logo will be svg that can change color. for mean time only 3
  // LOGO_COLORS
  logoColor: PropTypes.oneOf(Object.values(LOGO_COLORS)),
  color: PropTypes.string
}
