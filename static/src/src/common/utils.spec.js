import { List } from 'immutable'
import sinon from 'sinon'
import DefaultFemale from 'src/images/default_female.png'
import DefaultMale from 'src/images/default_male.png'
import DefaultOther from 'src/images/default_other.png'
import { GENDER } from '../enums'
import {
  checkImageURL,
  getErrorMessage,
  getLoaderImageForGender,
  numberBetweenMinMax,
  rewriteUrlImageForDefault,
  toAction,
  todayXyearsAgo,
  validateSize
} from './utils'

describe('UTILS validateSize', () => {
  it('should reject if image width is smaller than expected', () => {
    return validateSize({ height: 500, width: 250 }, 500)
      .catch(err => {
        expect(err).toBe('error.image_to_small')
      })
  })

  it('should reject if image height is smaller than expected', () => {
    return validateSize({ height: 250, width: 500 }, 500)
      .catch(err => {
        expect(err).toBe('error.image_to_small')
      })
  })

  it('should resolve if image dimension is bigger than expected', () => {
    return validateSize({ height: 512, width: 512 }, 500)
      .then(res => {
        expect(res).toBe()
      })
  })

  it('should resolve if image dimension is just as expected', () => {
    return validateSize({ height: 500, width: 500 }, 500)
      .then(res => {
        expect(res).toBe()
      })
  })
})

describe('UTILS numberBetweenMinMax', () => {
  it('should return max if num > max', () => {
    const result = numberBetweenMinMax(30, 0, 20)
    expect(result).toEqual(20)
  })
  it('should return min if num < min', () => {
    const result = numberBetweenMinMax(-10, 0, 20)
    expect(result).toEqual(0)
  })
  it('should return num if num between min and  max', () => {
    const result = numberBetweenMinMax(10, 0, 20)
    expect(result).toEqual(10)
  })
  it('should return num if max undefined', () => {
    const result = numberBetweenMinMax(30, 0)
    expect(result).toEqual(30)
  })
  it('should return min if num < min and max undefined', () => {
    const result = numberBetweenMinMax(-10, 0)
    expect(result).toEqual(0)
  })
  it('should return num if min,max undefined', () => {
    const result = numberBetweenMinMax(30)
    expect(result).toEqual(30)
  })
  it('should return num if min equals NaN and num < max', () => {
    const result = numberBetweenMinMax(-10, Number.NaN, 20)
    expect(result).toEqual(-10)
  })
})

describe('UTILS todayXyearsAgo', () => {

  it('should return year 2008 when today is 2018', () => {
    const clock = sinon.useFakeTimers(new Date(2018, 9, 1).getTime())
    expect(todayXyearsAgo(10).getFullYear()).toEqual(2008)
    clock.restore()
  })
})

describe('UTILS toAction', () => {
  it('should return object with type and empty payload', () => {
    const result = toAction('TEST_ACTION', {})
    expect(result).toEqual({
      type: 'TEST_ACTION', payload: {}
    })
  })
  it('should return object with type and not empty payload', () => {
    const result = toAction('TEST_ACTION', { test1: 'test1', test2: 'test2' })
    expect(result).toEqual({
      type: 'TEST_ACTION', payload: { test1: 'test1', test2: 'test2' }
    })
  })
})

describe('UTILS getLoaderImageForGender', () => {
  it('should return MALE image if passed male', () => {
    const image = getLoaderImageForGender(GENDER.MALE)
    expect(image).toEqual(DefaultMale)
  })

  it('should return FEMALE image if passed female', () => {
    const image = getLoaderImageForGender(GENDER.FEMALE)
    expect(image).toEqual(DefaultFemale)
  })

  it('should return OTHER image if passed other', () => {
    const image = getLoaderImageForGender(GENDER.OTHER)
    expect(image).toEqual(DefaultOther)
  })
  it('should return OTHER image if passed nothing', () => {
    const image = getLoaderImageForGender()
    expect(image).toEqual(DefaultOther)
  })
})

describe('UTILS rewriteUrlImageForDefault', () => {
  it('should return default_male if default url passed and gender is male', () => {
    const result = rewriteUrlImageForDefault('hydra/img/src/', GENDER.MALE)
    expect(result).toEqual('default_male')
  })
  it('should return default_female if default url passed and gender is female', () => {
    const result = rewriteUrlImageForDefault('hydra/img/src/', GENDER.FEMALE)
    expect(result).toEqual('default_female')
  })
  it('should return default_other if default url passed and gender is other', () => {
    const result = rewriteUrlImageForDefault('hydra/img/src/', GENDER.OTHER)
    expect(result).toEqual('default_other')
  })
  it('should return passed url whatever gender is', () => {
    const [ forMale, forFemale, forOther ] = [
      rewriteUrlImageForDefault('image_test.png', GENDER.MALE),
      rewriteUrlImageForDefault('image_test.png', GENDER.FEMALE),
      rewriteUrlImageForDefault('image_test.png', GENDER.OTHER)
    ]

    expect(forMale).toEqual('image_test.png')
    expect(forFemale).toEqual('image_test.png')
    expect(forOther).toEqual('image_test.png')
  })
  it('should return default_other if default url passed and gender is undefined', () => {
    const result = rewriteUrlImageForDefault('hydra/img/src/')
    expect(result).toEqual('default_other')
  })
  it('should return default_other if no params', () => {
    const result = rewriteUrlImageForDefault()
    expect(result).toEqual('default_other')
  })
})
describe('UTILS checkImageURL', () => {
  it('should return image for female if default_female passed', () => {
    const result = checkImageURL('default_female')
    expect(result).toEqual(DefaultFemale)
  })
  it('should return image for male if default_male passed', () => {
    const result = checkImageURL('default_male')
    expect(result).toEqual(DefaultMale)
  })
  it('should return image for other if default_other passed', () => {
    const result = checkImageURL('default_other')
    expect(result).toEqual(DefaultOther)
  })
  it('should return image for other if default_both passed', () => {
    const result = checkImageURL('default_both')
    expect(result).toEqual(DefaultOther)
  })
  it('should return url if not default image passed', () => {
    const result = checkImageURL('test_image.png')
    expect(result).toEqual('test_image.png')
  })
  it('should return image for male if nothing passed', () => {
    const result = checkImageURL()
    expect(result).toEqual(DefaultMale)
  })
})

describe('UTILS getErrorMessage', () => {
  it('should return empty string if no error passed', () => {
    const result = getErrorMessage()
    expect(result).toEqual('')
  })
  it('should return string if error with message passed', () => {
    const result = getErrorMessage({ message: 'test_123' })
    expect(result).toEqual('test_123')
  })
  it('should return string if error with get function passed', () => {
    const result = getErrorMessage({ get: function (sth) {return 'test_123'} })
    expect(result).toEqual('test_123')
  })
  it('should return string if error with data.data passed', () => {
    const result = getErrorMessage({ data: { data: 'test_123' } })
    expect(result).toEqual('test_123')
  })
  it('should return string if error with data.code passed', () => {
    const result = getErrorMessage({ data: { code: 'test_123' } })
    expect(result).toEqual('Oops. There is an error: test_123')
  })
  it('should return string if error is string', () => {
    const result = getErrorMessage('test_string_123')
    expect(result).toEqual('test_string_123')
  })
  it('should return string if error with get function w/o message passed', () => {
    const result = getErrorMessage({
      get: function (sth) {
        if(sth === 'data') {
          return new List(['error1', 'error2'])
        }
        else return null
      }
    })
    expect(result).toEqual(new List(['error1', 'error2']))
  })
  it('should return string if error with get function w/o message passed', () => {
    const result = getErrorMessage({
      get: function (sth) {
        if(sth === 'code') {
          return ('123')
        }
        else return null
      }
    })
    expect(result).toEqual('Oops. There is an error: 123')
  })
})
