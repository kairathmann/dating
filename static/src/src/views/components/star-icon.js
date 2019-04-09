import classnames from 'classnames'
import React from 'react'
import { srcByRetina } from 'src/common/utils'
import starImg1 from 'src/images/big-star.png'
import starImg2 from 'src/images/big-star@2x.png'
import starImg3 from 'src/images/big-star@3x.png'

export default function starIcon ({ className, ...props }) {
  return (
    <img
      src={ srcByRetina(starImg1, starImg2, starImg3) }
      alt='star icon'
      className={ classnames('star-icon', className) }
      { ...props }
    />
  )
}
