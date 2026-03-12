import { Link } from 'react-router-dom'
import Layout from '../components/Layout'

export default function Landing() {
  return (
    <Layout>
      <section className="landing-section">
        <h1 className="landing-title">
          <span className="landing-title-accent">OdontoFhir</span>
          <span className="landing-ai-accent">AI</span> Mapper
        </h1>

        <p className="landing-subtitle">
          Convertí fichas odontológicas, registros de alergias y consultas clínicas al
          estándar internacional <strong>HL7 FHIR</strong> de forma rápida y sencilla.
        </p>

        <div className="landing-actions">
          <Link to="/nueva-conversion" className="btn btn--primary btn--lg">
            Iniciar conversión
          </Link>

          <a
            href="https://odontofhirparaguay.netlify.app/"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn--outline btn--lg"
          >
            Ver documentación
          </a>
        </div>
      </section>
    </Layout>
  )
}