import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import Img from 'react-image'
import { checkImageURL } from 'src/common/utils'

import './avatar-round.css'

const AvatarRound = ({ photoURL, alt, imgClass, sizeInRem, floatHeight }) => {
  const size = `${sizeInRem}rem`

  const checkedUrl = checkImageURL(photoURL)
  return (
    <div
      style={ { height: size, width: size } }
      className={ classnames(
        'avatar-round container',
        imgClass,
        !!floatHeight && `height-${floatHeight}`
      ) }
    >
      { checkedUrl ?
        <Img
          className='avatar-round-image'
          src={ checkedUrl }
          alt={ alt }/>
        : null
      }
    </div>
  )
}
AvatarRound.propTypes = {
  photoURL: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]).isRequired,
  alt: PropTypes.string.isRequired,
  sizeInRem: PropTypes.number.isRequired,
  floatHeight: PropTypes.number,
}
AvatarRound.defaultProps = {
  sizeInRem: 10,
}

export default AvatarRound
