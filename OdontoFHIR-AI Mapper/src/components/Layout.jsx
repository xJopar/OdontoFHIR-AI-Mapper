import Header from './Header'

export default function Layout({ children }) {
  return (
    <div className="app-wrapper">
      <Header />

      <main className="main-content">
        {children}
      </main>
    </div>
  )
}