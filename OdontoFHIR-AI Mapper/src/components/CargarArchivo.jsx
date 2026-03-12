export default function FileUploader({ archivo, errorArchivo, onSeleccion, onLimpiar }) {
  const handleChange = (e) => {
    const file = e.target.files?.[0]

    if (!file) {
      onSeleccion(null)
      return
    }

    onSeleccion(file)
  }

  return (
    <div className="file-uploader">
      {!archivo ? (
        <label className="file-dropzone">
          <input
            type="file"
            className="file-input"
            onChange={handleChange}
            accept=".png,.jpg,.jpeg,.pdf,.csv,.txt"
          />

          <div className="file-dropzone-content">
            <p className="file-dropzone-title">Seleccionar archivo</p>
            <p className="file-dropzone-text">
              Podés subir una imagen (.png,.jpg) o un archivo de texto(.pdf,.csv,.txt).
            </p>
          </div>
        </label>
      ) : (
        <div className="file-selected">
          <div className="file-selected-info">
            <p className="file-selected-name">{archivo.name}</p>
            <p className="file-selected-size">
              {(archivo.size / 1024).toFixed(1)} KB
            </p>
          </div>

          <button
            type="button"
            className="btn btn--outline"
            onClick={onLimpiar}
          >
            Quitar archivo
          </button>
        </div>
      )}

      {errorArchivo && (
        <p className="file-error" role="alert">
          {errorArchivo}
        </p>
      )}
    </div>
  )
}