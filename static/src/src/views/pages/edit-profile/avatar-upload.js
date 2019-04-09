import React from 'react'
import Dropzone from 'react-dropzone'
import { FormattedMessage } from 'react-intl'

import { srcByRetina, validateSize } from 'src/common/utils'
import { ASYNC_STATES } from 'src/enums'
import placeholderImg1 from 'src/images/placeholder.png'
import placeholderImg2 from 'src/images/placeholder@2x.png'
import { AvatarRound, LunaLoader } from 'src/views/components'

import './avatar-upload.css'

export default function AvatarUpload (props) {

  const {
    photoURL,
    uploadUserImage,
    user,
    showError
  } = props

  const { imageUploadState } = user
  const duringUpload = (imageUploadState === ASYNC_STATES.DURING)
  const uploadFail = (imageUploadState === ASYNC_STATES.FAIL)

  let dropzoneRef

  return (
    <div className="avatar-upload">
      <div className="avatar-wrapper" onClick={ () => { (!photoURL && !duringUpload) && dropzoneRef.open() } }>

        <AvatarRound
          photoURL={ [ photoURL, srcByRetina(placeholderImg1, placeholderImg2) ] }
          alt={ 'Click to upload a new profile image' }
          imgClass={ 'top-avatar' }
          showSpinner={ imageUploadState === ASYNC_STATES.DURING }
        />
        { duringUpload && <div className='loader-wrapper'>
          <LunaLoader sizeInRem={ 3 }/>
        </div> }

      </div>


      { uploadFail && (
        <div className={ 'image-upload-error' }><FormattedMessage id={ 'avatar.error_uploading' }/></div>
      ) }

      <Dropzone
        ref={ (node) => { dropzoneRef = node } }
        onDrop={ (accepted, rejected) => {
          const [ file ] = accepted // accepting only one image for now

          const image = new Image()
          image.addEventListener('load', async () => {
            try {
              await validateSize(image, 500)
              uploadUserImage(file)
            } catch (err) {
              showError(err)
            }
          })
          const reader = new FileReader()

          reader.onload = function (e) {
            image.src = e.target.result
          }

          reader.readAsDataURL(file)
        } }
        style={ { display: 'none' } } // currently hidden. later maybe the image itself will be droppable
      />
      <button
        className='upload-button'
        type="button"
        onClick={ () => { dropzoneRef.open() } }
        disabled={ duringUpload }
      >
        <FormattedMessage id={ 'avatar.upload' }/>
      </button>
    </div>
  )
}
