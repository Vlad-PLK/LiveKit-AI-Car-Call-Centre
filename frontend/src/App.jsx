import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">Negresco Nice</div>
      </header>

      <main>
        <section className="hero">
          <h1>Get the best of your journey right now</h1>
          <div className="search-bar">
            <input type="text" placeholder='Enter your booking number'></input>
            <button>Search</button>
          </div>
        </section>

        <button className="support-button" onClick={handleSupportClick}>
          Talk with Alfred now !
        </button>
      </main>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App
