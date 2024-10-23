// function to handle properly hopeit api errors and throw a simplified error to UI
export const handleAPIErrorArrayBuffer = (error: any) => {
  console.log('handle api error')
  let message
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.log(error.response.status)
    // data is an array buffer, set generic responses
    message = `HA OCURRIDO UN ERROR INESPERADO (ERROR ${error.response.status}). Descripción: `
    if (error.response.status === 400) {
      message += 'Error en el requerimiento.'
    } else if (error.response.status === 404) {
      message += 'Archivo no encontrado.'
    } else if (error.response.status === 403) {
      message += 'No tiene permitido acceder al Archivo solicitado.'
    } else {
      message += 'Error desconocido.'
    }
  } else if (error.request) {
    // The request was made but no response was received
    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
    // http.ClientRequest in node.js
    console.log(error.request)
    message = 'HA OCURRIDO UN ERROR INESPERADO. NO SE HA RECIBIDO RESPUESTA DEL SERVIDOR'
  } else {
    // Something happened in setting up the request that triggered an Error
    console.log('Error', error.message)
    message = `HA OCURRIDO UN ERROR INESPERADO. Descripción: ${error.message}`
  }
  console.log(error)

  throw new Error(message)
}
