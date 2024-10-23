import dayjs from 'dayjs'
import {
  MACH_STATUS_PRODUCCION,
  MACH_STATUS_CAMBIO_MOLDE,
  MACH_STATUS_PREPARACION,
  MACH_STATUS_LIMPIEZA,
  MACH_STATUS_PREVENTIVO,
  MACH_STATUS_CORRECTIVO,
  MACH_STATUS_SIN_CONEXION,
  MACH_STATUS_PRODUCCION_DESC,
  MACH_STATUS_CAMBIO_MOLDE_DESC,
  MACH_STATUS_PREPARACION_DESC,
  MACH_STATUS_LIMPIEZA_DESC,
  MACH_STATUS_PREVENTIVO_DESC,
  MACH_STATUS_CORRECTIVO_DESC,
  MACH_STATUS_SIN_CONEXION_DESC,
} from '/@src/data/constants'

export const utils = {
  getInitials(str: string) {
    if (str) {
      const words_array = str.split(' ')
      let inits = ''
      if (words_array.length > 1) inits = words_array.map((word) => word[0]).join('')
      else inits = str.substring(0, 2)

      if (inits.length > 3) return inits.substring(0, 3).toUpperCase()

      return inits.toUpperCase()
    }
    return ''
  },
  // https://day.js.org/docs/en/display/format
  dateFmtDmyh(the_date: any) {
    if (the_date) {
      // const the_date2 = the_date.replace(/\+00:00$/, '')
      return dayjs(the_date).format('DD/MM/YYYY HH:mm')
    }
    return ''
  },
  dateFmtDmy(the_date: any) {
    if (the_date) {
      // const the_date2 = the_date.replace(/\+00:00$/, '')
      return dayjs(the_date).format('DD/MM/YYYY')
    }
    return ''
  },
  dateFmtDmyhs(the_date: any) {
    if (the_date) {
      // const the_date2 = the_date.replace(/\+00:00$/, '')
      return dayjs(the_date).format('DD/MM/YYYY HH:mm:ss')
    }
    return ''
  },
  isoToDmy(isoString: any) {
    if (isoString) {
      // remove timezone
      // const the_date2 = isoString.replace(/\+00:00$/, '')
      return dayjs(isoString).format('DD/MM/YYYY')
    }
    return ''
  },
  isoToDmyhm(isoString: any) {
    if (isoString) {
      // remove timezone
      // const the_date2 = isoString.replace(/\+00:00$/, '')
      return dayjs(isoString).format('DD/MM/YYYY HH:mm')
    }
    return ''
  },
  isoToDmhm(isoString: any) {
    if (isoString) {
      // remove timezone
      // const the_date2 = isoString.replace(/\+00:00$/, '')
      return dayjs(isoString).format('DD/MM HH:mm')
    }
    return ''
  },
  isoToDate(isoString: any) {
    if (isoString) {
      // remove timezone
      // const the_date2 = isoString.replace(/\+00:00$/, '')
      return dayjs(isoString).toDate()
    }
    return undefined
  },
  isoToGantt(isoString: any) {
    if (isoString) {
      return dayjs(isoString).format('YYYY-MM-DD HH:mm')
    }
    return ''
  },
  dateToGantt(the_date: any) {
    if (the_date) {
      return dayjs(the_date).format('YYYY-MM-DD HH:mm')
    }
    return ''
  },
  dmyToIso(dmyString: any) {
    // iso format: 2023-09-25T07:00:00-03:00
    if (dmyString) {
      const [day, month, year] = dmyString.split('/')
      return `${year}-${month}-${day}T00:00:00-03:00`
    }
    return ''
  },
  dmyhmToIso(dmyhmString: any) {
    // iso format: 2023-09-25T07:00:00-03:00
    if (dmyhmString) {
      const [datePart, timePart] = dmyhmString.split(' ')
      const [day, month, year] = datePart.split('/')
      const [hours, minutes] = timePart.split(':')
      return `${year}-${month}-${day}T${hours}:${minutes}:00-03:00`
    }
    return ''
  },
  /**
   * Format bytes as human-readable text.
   *
   * @param bytes Number of bytes.
   * @param si True to use metric (SI) units, aka powers of 1000. False to use
   *           binary (IEC), aka powers of 1024.
   * @param dp Number of decimal places to display.
   *
   * @return Formatted string.
   */
  humanFileSize(bytes: number, si: boolean = true, dp: number = 1) {
    const thresh = si ? 1000 : 1024

    if (Math.abs(bytes) < thresh) {
      return bytes + ' B'
    }

    const units = si
      ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
      : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    let u = -1
    const r = 10 ** dp

    do {
      bytes /= thresh
      ++u
    } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1)

    return bytes.toFixed(dp) + ' ' + units[u]
  },
  strShort(str: string, max: number = 15) {
    if (str) {
      return str.length <= max ? str : str.substring(0, max) + '...'
    }

    return ''
  },
  getNotificationImage(str: string) {
    let ret = 'icon-park-outline:info'
    if (str === 'error') {
      ret = 'icon-park-outline:caution'
    } else if (str === 'direct') {
      ret = 'icon-park-outline:message'
    } else if (str === 'upload') {
      ret = 'icon-park-outline:paperclip'
    } else if (str === 'mail') {
      ret = 'icon-park-outline:mail'
    } else if (str === 'call') {
      ret = 'feather:phone-call'
    } else if (str === 'papers') {
      ret = 'icon-park-outline:folder'
    } else if (str === 'event') {
      ret = 'icon-park-outline:calendar'
    } else if (str === 'state-change') {
      ret = 'icon-park-outline:refresh-one'
    } else if (str === 'estimation') {
      ret = 'icon-park-outline:chart-line'
    } else if (str === 'negotiation') {
      ret = 'icon-park-outline:imbalance'
    } else if (str === 'agreement') {
      ret = 'icon-park-outline:thumbs-up'
    } else if (str === 'decline') {
      ret = 'icon-park-outline:thumbs-down'
    }

    return ret
  },
  getNotificationColor(str: string) {
    let ret = 'blue'
    if (str === 'decline' || str === 'error') {
      ret = 'red'
    } else if (str === 'agreement') {
      ret = 'green'
    } else if (str === 'state-change') {
      ret = 'orange'
    } else if (str === 'event') {
      ret = 'purple'
    }
    return ret
  },
  getNotificationObjectDesc(item: any) {
    let ret = item.object_type
    if (item.object_name) ret += ' ' + item.object_name
    if (item.object_internal_id) ret += ' #' + item.object_internal_id

    return ret
  },
  getMachineStatusIcon(str: string) {
    let ret = 'icon-park-outline:battery-failure'
    if (str === MACH_STATUS_PRODUCCION) {
      ret = 'icon-park-outline:play'
    } else if (str === MACH_STATUS_CAMBIO_MOLDE) {
      ret = 'icon-park-outline:play-cycle'
    } else if (str === MACH_STATUS_PREPARACION) {
      ret = 'icon-park-outline:pause-one'
    } else if (str === MACH_STATUS_LIMPIEZA) {
      ret = 'icon-park-outline:clear'
    } else if (str === MACH_STATUS_PREVENTIVO) {
      ret = 'icon-park-outline:tool'
    } else if (str === MACH_STATUS_CORRECTIVO) {
      ret = 'icon-park-outline:tool'
    } else if (str === MACH_STATUS_SIN_CONEXION) {
      ret = 'icon-park-outline:help'
    }

    return ret
  },
  getMachineStatusColor(str: string) {
    let ret = 'light'
    if (str === MACH_STATUS_PRODUCCION) {
      ret = 'success'
    } else if (str === MACH_STATUS_CAMBIO_MOLDE) {
      ret = 'info'
    } else if (str === MACH_STATUS_PREPARACION) {
      ret = 'info'
    } else if (str === MACH_STATUS_LIMPIEZA) {
      ret = 'warning'
    } else if (str === MACH_STATUS_PREVENTIVO) {
      ret = 'warning'
    } else if (str === MACH_STATUS_CORRECTIVO) {
      ret = 'warning'
    } else if (str === MACH_STATUS_SIN_CONEXION) {
      ret = 'warning'
    }
    return ret
  },
  getMachineStatusDesc(str: string) {
    let ret = 'DESCONOCIDO'
    if (str === MACH_STATUS_PRODUCCION) {
      ret = MACH_STATUS_PRODUCCION_DESC
    } else if (str === MACH_STATUS_CAMBIO_MOLDE) {
      ret = MACH_STATUS_CAMBIO_MOLDE_DESC
    } else if (str === MACH_STATUS_PREPARACION) {
      ret = MACH_STATUS_PREPARACION_DESC
    } else if (str === MACH_STATUS_LIMPIEZA) {
      ret = MACH_STATUS_LIMPIEZA_DESC
    } else if (str === MACH_STATUS_PREVENTIVO) {
      ret = MACH_STATUS_PREVENTIVO_DESC
    } else if (str === MACH_STATUS_CORRECTIVO) {
      ret = MACH_STATUS_CORRECTIVO_DESC
    } else if (str === MACH_STATUS_SIN_CONEXION) {
      ret = MACH_STATUS_SIN_CONEXION_DESC
    }
    return ret
  },
  secondsToHourMinutes(seconds: number) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  },
  minutesToHourMinutes(minutes: number) {
    const hours = Math.floor(minutes / 60)
    const minutes2 = Math.floor(minutes % 60)
    if (hours > 0) {
      return `${hours}h ${minutes2}m`
    }
    return `${minutes2}m`
  },
}
