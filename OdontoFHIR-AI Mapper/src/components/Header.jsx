import { Link, NavLink } from 'react-router-dom'

export default function Header() {
  return (
    <header className="header">
      <div className="header-brand">
        <Link to="/" className="header-logo">
          <img src="/logo.svg" alt="OdontoFHIR logo" />
        </Link>
      </div>

      <nav className="header-nav" aria-label="Navegación principal">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `nav-link ${isActive ? 'nav-link--active' : ''}`
          }
        >
          Inicio
        </NavLink>

        <NavLink
          to="/nueva-conversion"
          className={({ isActive }) =>
            `nav-link ${isActive ? 'nav-link--active' : ''}`
          }
        >
          Nueva Conversión
        </NavLink>
        <a
          href="https://odontofhirpatients.netlify.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-link"
        >
          OdontoFHIR Patients ↗
        </a>
        <a
          href="https://odontofhirparaguay.netlify.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-link nav-link--docs"
        >
          Documentación
        </a>
      </nav>
    </header>
  )
}