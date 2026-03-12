import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import NuevaConversion from './pages/NuevaConversion'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/nueva-conversion" element={<NuevaConversion />} />
    </Routes>
  )
}