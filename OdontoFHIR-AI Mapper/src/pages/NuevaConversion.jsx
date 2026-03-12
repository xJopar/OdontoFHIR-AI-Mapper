import { useState, useEffect } from 'react'
import { convertirDocumento } from '../services/conversionService'
import Layout from '../components/Layout'
import FileUploader from '../components/CargarArchivo'
const API_URL = import.meta.env.VITE_API_URL;

const TIPOS_DOCUMENTO = [
  {
    value: 'paciente',
    label: 'Ficha de Paciente',
    descripcion: 'Registro de datos demográficos del paciente: identificación, nombre, fecha de nacimiento, sexo, dirección y contacto.',
    recurso: 'Patient',
  },
  {
    value: 'alergia',
    label: 'Alergias',
    descripcion: 'Registro de alergias o intolerancias del paciente a medicamentos, alimentos o sustancias.',
    recurso: 'AllergyIntolerance',
  },
  {
    value: 'consulta',
    label: 'Consulta Clínica',
    descripcion: 'Registro de una consulta odontológica que puede incluir motivo de consulta, hallazgos clínicos, diagnóstico y procedimientos.',
    recurso: 'Encounter',
  },
]
export default function NuevaConversion() {
  const [intentoEnviar, setIntentoEnviar] = useState(false)
  const [tipoSeleccionado, setTipoSeleccionado] = useState('')
  const [archivo, setArchivo] = useState(null)
  const [errorArchivo, setErrorArchivo] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resultado, setResultado] = useState(null)
  const [backendStatus, setBackendStatus] = useState('verificando')
  const [backendMessage, setBackendMessage] = useState('Verificando conexión con el backend...')

  useEffect(() => {
    const verificarBackend = async () => {
      try {
        const response = await fetch(`${API_URL}/health`)
        const data = await response.json()

        if (response.ok && data.status === 'ok') {
          setBackendStatus('conectado')
          setBackendMessage('Backend conectado')
        } else {
          setBackendStatus('error')
          setBackendMessage('Backend disponible, pero respondió de forma inesperada')
        }
      } catch (error) {
        console.error('Error al verificar backend:', error)
        setBackendStatus('error')
        setBackendMessage('No se pudo conectar con el backend')
      }
    }

    verificarBackend()
  }, [])
  // Guarda el archivo seleccionado y limpia errores previos.
  const manejarSeleccionArchivo = (file) => {
    if (!file) {
      setArchivo(null)
      return
    }

    setErrorArchivo('')
    setArchivo(file)
  }

  // Limpia solo el archivo cargado.
  const limpiarArchivo = () => {
    setArchivo(null)
    setErrorArchivo('')
  }

  // Reinicia todo para empezar una nueva conversión.
  const handleNuevaConversion = () => {
    setTipoSeleccionado('')
    setArchivo(null)
    setErrorArchivo('')
    setError('')
    setResultado(null)
    setLoading(false)
  }

  // Descarga el resultado como archivo JSON.
  const descargarJson = () => {
    if (!resultado) return

    const contenido = JSON.stringify(resultado, null, 2)
    const blob = new Blob([contenido], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    const enlace = document.createElement('a')
    enlace.href = url
    enlace.download = 'resultado-fhir.json'
    document.body.appendChild(enlace)
    enlace.click()
    document.body.removeChild(enlace)

    URL.revokeObjectURL(url)
  }

  // Llamda al backend
  const handleProcesar = async (e) => {
    e.preventDefault()
    setIntentoEnviar(true)

    if (!tipoSeleccionado || !archivo) {
      setError('Completá los campos obligatorios para continuar.')
      return
    }

    setError('')
    setLoading(true)

    try {
      const data = await convertirDocumento(tipoSeleccionado, archivo)
      setResultado(data)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Ocurrió un error al procesar el documento.')
    } finally {
      setLoading(false)
    }
  }

  const puedeEnviar = tipoSeleccionado && archivo && !loading

  return (
    <Layout>
      <section className="page-header">
        <h1 className="page-title">Nueva conversión</h1>
        <p className="page-subtitle">
          Seleccioná el tipo de documento, subí el archivo y generá el recurso FHIR.
        </p>

        <div className={`backend-status backend-status--${backendStatus}`}>
          {backendMessage}
        </div>
      </section>

      {resultado ? (
        <section className="result-section card">
          <div className="result-header">
            <div className="result-badge result-badge--success">
              Conversión exitosa
            </div>

            <p className="result-resource-type">
              Recurso generado:{' '}
              <strong>{resultado.resourceType || 'Sin resourceType'}</strong>
            </p>
          </div>

          <div className="result-actions">
            <button
              type="button"
              className="btn btn--outline"
              onClick={descargarJson}
            >
              Descargar JSON
            </button>

            <button
              type="button"
              className="btn btn--primary"
              onClick={handleNuevaConversion}
            >
              Nueva conversión
            </button>
          </div>

          <pre className="result-json">
            {JSON.stringify(resultado, null, 2)}
          </pre>
        </section>
      ) : (
        <form className="conversion-form card" onSubmit={handleProcesar} noValidate>
          <fieldset className="form-fieldset">
            <legend className="form-legend">1. Tipo de documento</legend>

            <div
              className={`document-type-grid ${intentoEnviar && !tipoSeleccionado
                  ? 'document-type-grid--error'
                  : ''
                }`}
            >
              {TIPOS_DOCUMENTO.map((tipo) => (
                <label
                  key={tipo.value}
                  className={`document-type-option ${tipoSeleccionado === tipo.value
                      ? 'document-type-option--selected'
                      : ''
                    }`}
                >
                  <input
                    type="radio"
                    name="tipoDocumento"
                    value={tipo.value}
                    checked={tipoSeleccionado === tipo.value}
                    onChange={() => setTipoSeleccionado(tipo.value)}
                    className="document-type-input"
                  />

                  <div className="document-type-content">
                    <span className="document-type-label">{tipo.label}</span>
                    <span className="document-type-description">
                      {tipo.descripcion}
                    </span>
                    <span className="document-type-resource">
                      Recurso: {tipo.recurso}
                    </span>
                  </div>
                </label>
              ))}
            </div>

            {intentoEnviar && !tipoSeleccionado && (
              <p className="field-error">Seleccioná un tipo de documento.</p>
            )}
          </fieldset>

          <fieldset className="form-fieldset">
            <legend className="form-legend">2. Archivo a convertir</legend>

            <FileUploader
              archivo={archivo}
              errorArchivo={errorArchivo}
              onSeleccion={manejarSeleccionArchivo}
              onLimpiar={limpiarArchivo}
            />

            {intentoEnviar && !archivo && (
              <p className="field-error">Subí un archivo para continuar.</p>
            )}
          </fieldset>

          {error && (
            <div className="alert alert--error" role="alert">
              {error}
            </div>
          )}

          <div className="form-submit">
            <button
              type="submit"
              className="btn btn--primary btn--full"
              disabled={loading}
            >
              {loading ? 'Procesando...' : 'Procesar documento'}
            </button>

            {!loading && (
              <p className="form-hint">
                Completá el tipo de documento y el archivo antes de procesar.
              </p>
            )}
          </div>
        </form>
      )}
    </Layout>
  )
}