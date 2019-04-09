import { GENDER } from 'src/enums'
import DefaultFemale from 'src/images/default_female.png'
import DefaultMale from 'src/images/default_male.png'
import DefaultOther from 'src/images/default_other.png'

export function getErrorMessage (error) {
  if (!error) {
    return ''
  }

  if (error.message || (typeof error.get === 'function' && error.get('message'))) {
    return error.message || error.get('message')
  }

  if (error.data) {
    if (error.data.data && !isEmptyObject(error.data.data)) {
      return error.data.data
    } else if (error.data.code && !isEmptyObject((error.data.code))) {
      // TODO: INTL
      return `Oops. There is an error: ${error.data.code}`
    }
  }

  if (!error.get) {
    return error
  }

  if (error.get('data') && error.get('data').size > 0) {
    return error.get('data')
  } else if (error.get('code')) {
    return `Oops. There is an error: ${error.get('code')}`
  } else {
    return error
  }
}

function isEmptyObject (obj) {
  return Object.keys(obj).length === 0 && obj.constructor === Object
}

export function numberBetweenMinMax (num, min, max) {
  if (typeof max !== 'undefined' && !isNaN(max) && num > max) { return max }
  if (typeof min !== 'undefined' && !isNaN(min) && num < min) { return min }
  return num
}

export function srcByRetina (first, second, third) {
  const ratio = window.devicePixelRatio
  if (ratio >= 3) {
    return third || second || first
  } else if (ratio >= 2) {
    return second || first
  }
  return first
}

export function getDateStrs (date) {
  const locale = 'en-us'
  const [ dayInMonth, monthName, year, timeStr ] = [
    date.getDate(),
    date.toLocaleString(locale, { month: 'short' }),
    date.getFullYear(),
    date.toLocaleString(locale, { hour: '2-digit', minute: '2-digit' }),
  ]

  const dayStr = `${monthName} ${dayInMonth} ${year}`

  return [ dayStr, timeStr ]

}

/**
 *
 * @param date: Date
 * @returns {string} yyyy-mm-dd
 */
export function dateToYYYYMMDDdashStr (date) {
  return date.toISOString().slice(0, 10)
}

export function todayXyearsAgo (yearsAgo) {
  const date = new Date()
  date.setYear(date.getFullYear() - yearsAgo)
  return date
}

export function todayXyearsAgoAsStr (yearsAgo) {
  return dateToYYYYMMDDdashStr(todayXyearsAgo(yearsAgo))
}

export function toAction (type, payload) { return { type, payload } }

/**
 *
 * @param avatar_url - server response
 * @returns {{photoURL: string}} usable full url. as obj so it will keep same naming across app
 */
export function avatarUrlToPhotoUrlObj (avatarUrl) {
  // avatar
  return {
    photoURL: `${avatarUrl}`
  }
}

export function getLoaderImageForGender (gender = GENDER.OTHER) {
  switch (gender) {
    case GENDER.MALE:
      return DefaultMale
    case GENDER.FEMALE:
      return DefaultFemale
    default:
      return DefaultOther
  }
}

export function rewriteUrlImageForDefault (photoUrl = 'hydra/img/src/', gender = GENDER.OTHER) {
  if (photoUrl.includes('hydra/img/src/')) {
    switch (gender) {
      case GENDER.MALE:
        return 'default_male'
      case GENDER.FEMALE:
        return 'default_female'
      default:
        return 'default_other'
    }
  } else {
    return photoUrl
  }
}

export function checkImageURL (photoUrl = 'default_male') {
  if (photoUrl.includes('default_male')) {return DefaultMale}
  if (photoUrl.includes('default_female')) {return DefaultFemale}
  if (photoUrl.includes('default_other')) {return DefaultOther}
  if (photoUrl.includes('default_both')) {return DefaultOther}
  else {
    return photoUrl
  }
}

export function validateSize (image, minSize) {
  return new Promise((resolve, reject) => {
    if (image.width < minSize || image.height < minSize) {
      reject('error.image_to_small')
    } else {
      resolve()
    }
  })
}

export function getAge (birthDateString) {
  const today = new Date()
  const birthDate = new Date(birthDateString)
  let age = today.getFullYear() - birthDate.getFullYear()
  const m = today.getMonth() - birthDate.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}
