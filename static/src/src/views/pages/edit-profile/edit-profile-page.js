import classNames from 'classnames'
import range from 'lodash.range'
import moment from 'moment'
import PropTypes from 'prop-types'
import 'rc-slider/assets/index.css'
import React, { Component } from 'react'
import 'react-datepicker/dist/react-datepicker.css'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import Select from 'react-select'
import Textarea from 'react-textarea-autosize'

import smartcrop from 'smartcrop'
import { getAge, todayXyearsAgoAsStr } from 'src/common/utils'
import { loadEditDataForUser, startUploadingUserImage, uploadUserImage } from 'src/editUserData/actions'
import { GENDER } from 'src/enums'
import { notificationActions } from 'src/notification'
import routes, { toPath } from 'src/routes'
import { userActions } from 'src/user'
import { isUserExist, isUserMissingCriticalDetails } from 'src/user/user'
import { BackButton, Header, HeaderAction, HeaderTitle, LunaAgeSlider, LunaInput } from 'src/views/components'
import 'tracking/build/tracking'
import 'tracking/build/data/face'

import AvatarUpload from './avatar-upload'
import './edit-profile-page.css'

export class EditProfilePage extends Component {

  genderDefaults = [
    { value: GENDER.MALE, label: 'Man' },
    { value: GENDER.FEMALE, label: 'Woman' },
    { value: GENDER.OTHER, label: 'Non-binary' }
  ]

  sexualityDefaults = [
    { value: GENDER.MALE, label: 'Men' },
    { value: GENDER.FEMALE, label: 'Women' },
    { value: GENDER.BOTH, label: 'Everyone' }
  ]

  constructor (props) {
    super(props)

    this.state = {
      bio: '',
      tagline: '',
      age: 0,
      ageDefaults: range(18, 80).map(n => {return { value: n, label: n.toString() }}),
      birthday: moment(),
      inboxSizeChanged: false,
      photoURL: '',
      seekingAgeFrom: 21,
      seekingAgeTo: 36,
      gender: -1,
      sexuality: -1,
      firstName: '',
      emptyNickname: false,
      imageError: '',
      ageError: false
    }

    this.croppedPreview = null
    this.croppedPreviewRef = element => {
      this.croppedPreview = element
    }
  }

  componentWillMount () {
    this.props.loadEditDataForUser(this.props.user.id)
    this.updateStateByProps(this.props)
  }

  componentWillReceiveProps (nextProps) {
    this.updateStateByProps(nextProps)
  }

  handleAgeChange = (event) => {
    this.setState({
      seekingAgeFrom: event[ 0 ],
      seekingAgeTo: event[ 1 ],
    })
  }

  renderAgeSlider () {
    return <LunaAgeSlider
      values={ [ this.state.seekingAgeFrom, this.state.seekingAgeTo ] }
      onChange={ this.handleAgeChange }/>
  }

  updateStateByProps (props) {
    const { user } = props
    this.setState({
      age: user.age || 0,
      bio: user.bio || '',
      tagline: user.tagline || '',
      gidIs: user.gidIs || 1,
      gidSeeking: user.gidSeeking || 1,
      birthday: user.birthday,
      // have real data
      name: user.name || '',
      email: user.email || '',
      photoURL: user.photoURL || '',
      inboxSizeChanged: false,
      seekingAgeFrom: user.seekingAgeFrom || 18,
      seekingAgeTo: user.seekingAgeTo || 80,
      gender: user.gidIs || 0,
      sexuality: user.gidSeeking || 0,
      firstName: user.firstName || ''
    })
  }

  onImageLoaded = (content) => {
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
        this.props.uploadUserImage(content, result.topCrop)
      })
    }, 500)

  }

  render () {
    const { user, intl } = this.props
    const {
      seekingAgeFrom,
      seekingAgeTo,
      photoURL,
      preview,
      ageError
    } = this.state

    const isUpdatingExistingDetails = isUserExist(user) && !isUserMissingCriticalDetails(user)
    return (
      <div className='edit-profile-page'>
        { isUpdatingExistingDetails && (
          <Header equalSidesForStrictCenter>
            <BackButton destination={ toPath(routes.viewProfile) }/>
            <HeaderTitle title={ intl.formatMessage({ id: 'edit.header_title' }) }/>
            <HeaderAction title={ ageError ? '' : intl.formatMessage({ id: 'common.save' }) } onClick={ this.handleSubmit }/>
          </Header>
        ) }
        <div className='edit-profile-container'>
          <div className="name-and-photo">
            <h1><FormattedMessage id={ 'common.welcome' }/> { this.props.user.firstName }</h1>

            <AvatarUpload
              uploadUserImage={ this.onImageLoaded }
              user={ user }
              photoURL={ photoURL }
              showError={ this.handleImageError }
            />
            { this.state.imageError && <p className='red'><FormattedMessage id={ this.state.imageError }/></p> }
            <img ref={ this.croppedPreviewRef } style={ { width: '100%', display: 'none' } } src={ preview }
                 alt='Avatar preview'/>
          </div>
          <div>
            { this.renderTextInput('firstName', intl.formatMessage({ id: 'fill.about.nickname' })) }
            { this.state.emptyNickname && <p className='red'><FormattedMessage id={ 'error.empty_nickname' }/></p> }
            { this.renderBirthDayInput() }
          </div>
          { ageError && (
            <p className={'red'}>You are under 18 years old. You cannot use Luna.</p>
          )}
          <div>
            <p className='description'><FormattedMessage id={ 'fill.gender.gender_prompt' }/></p>
            { this.renderSelect(intl.formatMessage({ id: 'fill.gender.gender_prompt' }),
              'gender',
              'Choose',
              this.genderDefaults) }
            <p className='description'><FormattedMessage id={ 'fill.gender.sexuality_prompt' }/></p>
            { this.renderSelect(intl.formatMessage({ id: 'fill.gender.sexuality_prompt' }),
              'sexuality',
              'Choose',
              this.sexualityDefaults) }
          </div>
          <div>
            <span className='description'><FormattedMessage id={ 'edit.age_preferences' }/></span>
            <div className='age-container'>
              <span>{ seekingAgeFrom }</span>-
              <span>{ seekingAgeTo }</span>
            </div>
          </div>
          <div>
            { this.renderAgeSlider() }
          </div>
          <div>
            <span className='description'><FormattedMessage id={ 'edit.daily_limit' }/></span>
            <div className='inboxSize-container'>
              <span><FormattedMessage id={ 'edit.up_to' } values={ { 'inboxSize': 10 } }/></span>
            </div>
          </div>

        </div>
        <div className="text-areas">
          <div className="textarea-description-container">
            <span className='description'><FormattedMessage id={ 'edit.tagline' }/></span>
          </div>
          <div>{ this.renderTextArea('tagline', intl.formatMessage({ id: 'edit.tagline' })) }</div>

          <div className="textarea-description-container">
            <span className='description'><FormattedMessage id={ 'edit.bio' }/></span>
          </div>
          <div>{ this.renderTextArea('bio', intl.formatMessage({ id: 'edit.biography' })) }</div>
        </div>

        { !isUpdatingExistingDetails && (
          <div className="submit-btn-container">
            { this.renderInitialSubmit() }
          </div>
        ) }

        <div className='manage-account-container'>
          <p><FormattedMessage id={ 'disable.prompt1' }/> <Link to={ '/' + routes.disable }><FormattedMessage
            id={ 'disable.prompt2' }/></Link> <FormattedMessage id={ 'disable.prompt3' }/></p>
        </div>
      </div>
    )
  }

  renderBirthDayInput () {
    const bdFieldName = 'birthday'
    return (
      <div className="input-group">
        <input
          className='input'
          type='date'
          name={ bdFieldName }
          value={ this.state[ bdFieldName ] }
          placeholder='Birthday'
          ref={ e => this[ bdFieldName + 'Input' ] = e }
          min={ todayXyearsAgoAsStr(90) }
          max={ todayXyearsAgoAsStr(18) }
          onChange={ this.handleChangeDate }
        />
      </div>
    )
  }

  renderTextInput (fieldName, placeholder) {
    return <LunaInput
      fieldName={ fieldName }
      placeholder={ placeholder }
      value={ this.state[ fieldName ] }
      onChange={ this.handleChange }
    />
  }

  renderInput (fieldName, placeholder) {
    return (<input
      type='number'
      name={ fieldName }
      value={ this.state[ fieldName ] }
      placeholder={ placeholder }
      ref={ e => this[ fieldName + 'Input' ] = e }
      onChange={ this.handleChange }
    />)
  }

  renderTextArea (fieldName, placeholder) {
    return (
      <Textarea
        className={ classNames('textarea', fieldName) }
        name={ fieldName }
        value={ this.state[ fieldName ] }
        placeholder={ placeholder }
        ref={ e => this[ fieldName + 'Input' ] = e }
        onChange={ this.handleChange }
      />)
  }

  renderSelect (title, fieldName, placeholder, options) {
    return (
      <div className='input-group'>
        <Select
          type='text'
          name={ fieldName }
          value={ this.state[ fieldName ] }
          placeholder={ title }
          ref={ e => this[ fieldName + 'Input' ] = e }
          onChange={ (e) => {
            let val = null
            if (e) { val = e.value }
            this.setState({ [ fieldName ]: val })
          } }
          options={ options }
          noResultsText={ 'Nothing found' }
          searchable={ false }
          clearable={ false }
        />
      </div>)
  }

  renderInitialSubmit () {
    const { user } = this.props

    const updatedUser = Object.assign({}, user, this.state)
    const disabled = isUserMissingCriticalDetails(updatedUser)
    return (
      <button
        className='button submit-btn button-main'
        onClick={ !disabled ? this.handleSubmit : undefined }
        disabled={ disabled }
      >
        <FormattedMessage id={ 'edit.lets_go' }/>
      </button>)
  }

  validate = () => {
    return getAge(this.state.birthday) >= 18
  }

  handleImageError = err => {
    this.setState({
      imageError: err
    })
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

  handleChangeDate = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
      ageError: getAge(e.target.value) < 18
    })
  }

  handleSubmit = async (event) => {
    event && event.preventDefault()

    if (!this.state.firstName) {
      return this.setState({ emptyNickname: true })
    }

    await this.props.updateUser({
      'bio': this.state.bio,
      'tagline': this.state.tagline,
      'email': this.state.email,
      'seeking_age_from': parseInt(this.state.seekingAgeFrom, 10),
      'seeking_age_to': parseInt(this.state.seekingAgeTo, 10),
      'first_name': this.state.firstName,
      'gid_is': this.state.gender,
      'gid_seeking': this.state.sexuality,
      'birth_date': this.state.birthday
    })

    if (this.state.inboxSizeChanged) {
      await this.props.updateUserInboxSize(parseInt(this.state.inboxSize, 10))
    }
    this.props.history.push(routes.recommendations)
  }

}

EditProfilePage.propTypes = {
  auth: PropTypes.object.isRequired,
  user: PropTypes.shape({
    bio: PropTypes.string,
    firstName: PropTypes.string,
    photoURL: PropTypes.string,
    tagline: PropTypes.string,
    viewerHid: PropTypes.string,
    targetHid: PropTypes.string,
    age: PropTypes.number,
    seekingAgeFrom: PropTypes.number,
    seekingAgeTo: PropTypes.number,
    email: PropTypes.string,
  }).isRequired,
  loadEditDataForUser: PropTypes.func.isRequired,
  uploadUserImage: PropTypes.func.isRequired,
  updateUser: PropTypes.func.isRequired,
  updateUserInboxSize: PropTypes.func.isRequired,
  showError: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.userEditData.user.toJS(),
    auth: state.auth,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  notificationActions,
  { loadEditDataForUser, uploadUserImage, startUploadingUserImage }
)

export default injectIntl(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(EditProfilePage))
