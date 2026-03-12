const API_URL = import.meta.env.VITE_API_URL;

export async function convertirDocumento(tipo, archivo) {
  const formData = new FormData()
  formData.append('tipo', tipo)
  formData.append('archivo', archivo)

  console.log('Enviando request a /convertir...')

  const response = await fetch(`${API_URL}/convertir`, {
    method: 'POST',
    body: formData,
  })

  const data = await response.json()

  console.log('Status HTTP:', response.status)
  console.log('Respuesta JSON:', data)

  if (!response.ok) {
    const message =
      typeof data?.detail === 'string'
        ? data.detail
        : data?.detail?.message || 'Error en la conversión.'

    throw new Error(message)
  }

  return data
}