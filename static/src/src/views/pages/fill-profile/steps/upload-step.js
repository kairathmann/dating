import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Dropzone from 'react-dropzone'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import smartcrop from 'smartcrop'

import { srcByRetina } from 'src/common/utils'
import { ASYNC_STATES } from 'src/enums'
import { startUploadingUserImage, uploadUserImage } from 'src/fillUserData/actions'
import placeholderImg2 from 'src/images/placeholder@2x.png'
import { AvatarRound, LunaLoader, LunaSubmit } from 'src/views/components'
import { validateSize } from 'src/common/utils'

class UploadStep extends Component {
  constructor (props) {
    super(props)
    this.state = {
      preview: '',
      imageError: ''
    }

    this.croppedPreview = null
    this.croppedPreviewRef = element => {
      this.croppedPreview = element
    }
  }

  onImageLoaded = async (content) => {
    this.setState({
      imageError: ''
    })
    this.props.startUploadingUserImage()
    const reader = new FileReader()
    reader.onload = (e) => {
      this.setState({
        preview: e.target.result
      })
    }

    reader.readAsDataURL(content)

    setTimeout(async () => {
      const tracker = new window.tracking.ObjectTracker('face')
      window.tracking.track(this.croppedPreview, tracker)
      tracker.on('track', async (event) => {
        const options = {
          width: 50,
          height: 50,
          minScale: 1.0,
          ruleOfThirds: false,
          boost: event.data.map((rec) => {
            return {
              ...rec,
              weight: 1.0
            }
          })
        }
        const result = await smartcrop.crop(this.croppedPreview, options)
        await this.props.uploadUserImage(content, result.topCrop)
      })
    }, 500)
  }

  render () {
    const { user } = this.props
    const { photoURL, imageUploadState } = user

    const duringUpload = (imageUploadState === ASYNC_STATES.DURING)
    const uploadFail = (imageUploadState === ASYNC_STATES.FAIL)

    let dropzoneRef

    return (
      <div className='step'>
        <h1 className='title'><FormattedMessage id={'fill.upload.header'}/></h1>
        <form onSubmit={ (event) => this.handleSubmit(event) } noValidate>
          <div className="name-and-photo">
            <div className="avatar-upload">
              <div className="avatar-wrapper" onClick={ () => { !duringUpload && dropzoneRef.open() } }>

                <AvatarRound
                  photoURL={ [ photoURL, srcByRetina(placeholderImg2) ] }
                  alt={ 'Click to upload a new profile image' }
                  sizeInRem={ 30 }
                  imgClass={ 'top-avatar' }
                />
                { duringUpload && <div className='loader-wrapper'>
                  <LunaLoader sizeInRem={ 3 }/>
                </div> }

              </div>


              { uploadFail && (
                <div className={ 'image-upload-error' }><FormattedMessage id={'fill.upload.error'}/></div>
              ) }

              <Dropzone
                ref={ (node) => { dropzoneRef = node } }
                onDrop={ (accepted) => {
                  const [ file ] = accepted // accepting only one image for now

                  const image = new Image()
                  image.addEventListener('load', async () => {
                    try {
                      await validateSize(image, 500)
                      this.onImageLoaded(file)
                    } catch (err) {
                      this.showError(err)
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
              { this.state.imageError && <p className='red'><FormattedMessage id={this.state.imageError}/></p>}
            </div>
            <img ref={ this.croppedPreviewRef }
                 alt='preview'
                 style={ { width: '100%', display: 'none' } }
                 src={ this.state.preview }/>
          </div>
          { this.renderSubmit() }
        </form>
      </div>
    )
  }

  renderSubmit () {
    return <LunaSubmit/>
    // return (
    //   <input className='button submit-btn' type='submit' value='Next'/>)
  }

  showError = err => {
    this.setState({
      imageError: err
    })
  }

  handleSubmit = (event) => {
    event && event.preventDefault()

    this.props.onUpdate({})
  }
}

UploadStep.propTypes = {
  onUpdate: PropTypes.func.isRequired
}

const mapStateToProps = (state) => {
  return {
    user: state.fill.user,
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  uploadUserImage,
  startUploadingUserImage
}

export default connect(mapStateToProps, mapDispatchToProps)(UploadStep)
