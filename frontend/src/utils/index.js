import { toast } from 'frappe-ui'
export function createToast(options) {
  toast({
    position: 'bottom-right',
    ...options,
  })
}

export function getCalendarDates(month = 0, year = 0) {
  let daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  let firstDay = new Date(year, month, 1)
  let leftPadding = firstDay.getDay()
  // debugger
  let datesInCurrentMonth = getCurrentMonthDates(firstDay)
  let datesInPreviousMonth = getBeforeDates(firstDay, leftPadding)
  let datesTillNow = [...datesInPreviousMonth, ...datesInCurrentMonth]
  let datesInNextMonth = getNextMonthDates(datesTillNow)
  let allDates = [...datesTillNow, ...datesInNextMonth]

  return allDates

  function getCurrentMonthDates(date) {
    let month = date.getMonth()
    if (month == 1 && isLeapYear(date)) {
      daysInMonth[month] = 29
    }

    let numberOfDays = daysInMonth[month] + 1
    let allDates = getDatesAfter(date, 1, numberOfDays)
    return allDates
  }

  function getBeforeDates(firstDay, leftPadding) {
    let allDates = getDatesAfter(firstDay, 0, leftPadding, -1)
    allDates = allDates.reverse()
    return allDates
  }

  function getNextMonthDates(currentAndPreviousMonthDates) {
    let lengthOfDates = currentAndPreviousMonthDates.length
    let lastDate = currentAndPreviousMonthDates[lengthOfDates - 1]
    let diff = 42 - lengthOfDates + 1

    let allDates = getDatesAfter(lastDate, 1, diff, 1, true)
    return allDates
  }

  function getDatesAfter(
    date,
    startIndex,
    counter,
    stepper = 1,
    getNextMonthDates = false
  ) {
    let allDates = []
    for (let index = startIndex; index < counter; index++) {
      let tempDate = new Date(
        date.getFullYear(),
        getNextMonthDates ? date.getMonth() + 1 : date.getMonth(),
        index * stepper
      )
      // debugger
      allDates.push(tempDate)
    }
    // debugger
    return allDates
  }

  function isLeapYear(date) {
    let year = date.getFullYear()
    return year % 400 === 0 || (year % 100 !== 0 && year % 4 === 0)
  }
}

export function groupBy(obj, fn) {
  if (typeof fn !== 'function') throw new Error(`${fn} should be a function`)
  return Object.keys(obj).reduce((acc, key) => {
    const group = fn(obj[key])
    if (!acc[group]) {
      acc[group] = []
    }
    acc[group].push(obj[key])
    return acc
  }, {})
}

// Time constants in milliseconds
export const TIME_CONSTANTS = {
  MILLISECONDS_PER_MINUTE: 60000,
  MILLISECONDS_PER_HOUR: 3600000,
  MILLISECONDS_PER_DAY: 86400000,
  MILLISECONDS_PER_WEEK: 604800000,
}

/**
 * Parse currency string and extract numeric value
 * @param {string} currencyString - Currency string like "KES 1,234.56"
 * @returns {number} - Numeric value
 */
export function parseCurrencyValue(currencyString) {
  if (!currencyString) return 0
  return parseFloat(currencyString.replace(/[^0-9.-]+/g, '') || 0)
}

/**
 * Format a number as currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: 'KES')
 * @returns {string} - Formatted currency string
 */
export function formatCurrency(amount, currency = 'KES') {
  return `${currency} ${amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`
}

/**
 * Format a date string for display
 * @param {string|Date} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
export function formatDate(date, options = {}) {
  if (!date || date === '-') return '-'
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }
  return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options })
}

/**
 * Get relative time string (e.g., "5 minutes ago")
 * @param {string|Date} datetime - Date/time to format
 * @returns {string} - Relative time string
 */
export function getRelativeTime(datetime) {
  if (!datetime) return ''
  const date = new Date(datetime)
  const now = new Date()
  const diff = now - date

  const { MILLISECONDS_PER_MINUTE, MILLISECONDS_PER_HOUR, MILLISECONDS_PER_DAY, MILLISECONDS_PER_WEEK } = TIME_CONSTANTS

  if (diff < MILLISECONDS_PER_HOUR) {
    const minutes = Math.floor(diff / MILLISECONDS_PER_MINUTE)
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`
  }

  if (diff < MILLISECONDS_PER_DAY) {
    const hours = Math.floor(diff / MILLISECONDS_PER_HOUR)
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`
  }

  if (diff < MILLISECONDS_PER_WEEK) {
    const days = Math.floor(diff / MILLISECONDS_PER_DAY)
    return `${days} day${days !== 1 ? 's' : ''} ago`
  }

  return formatDate(date)
}
