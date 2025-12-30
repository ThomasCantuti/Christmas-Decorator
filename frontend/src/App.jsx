import { useState } from 'react'
import './index.css'

function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setResult(null)
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError("Please upload an image first!")
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('image', file)
    if (text) formData.append('prompt', text)

    try {
      const response = await fetch('http://localhost:8000/api/decorate', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Something went wrong')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-card animate-fade-in">
      <h1 className="title">Christmas Decorator</h1>
      <p className="subtitle">Transform your space into a winter wonderland with AI ✨</p>

      {!result && (
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <div
              className="file-drop-zone"
              onClick={() => document.getElementById('file-input').click()}
            >
              {preview ? (
                <img src={preview} alt="Preview" style={{ maxHeight: '300px', borderRadius: '12px' }} />
              ) : (
                <>
                  <p style={{ fontSize: '2rem', margin: 0 }}>📷</p>
                  <p>Click to upload your room photo</p>
                </>
              )}
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>

            <input
              type="text"
              className="text-input"
              placeholder="Optional: What kind of decoration do you want?"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          {error && <div style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{error}</div>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="loader" style={{ width: '20px', height: '20px', border: '3px solid white', borderBottomColor: 'transparent', marginRight: '10px' }}></span>
                Decorating...
              </>
            ) : 'Decorate My Room 🎄'}
          </button>
        </form>
      )}

      {result && (
        <div className="animate-fade-in">
          <div className="result-container">
            <div>
              <h3>Before</h3>
              <img src={preview} className="image-preview" alt="Original" />
            </div>
            <div>
              <h3>After</h3>
              <img src={`data:image/jpeg;base64,${result.image_base64}`} className="image-preview" alt="Decorated" />
            </div>
          </div>

          <div className="explanation-card" style={{ marginTop: '2rem' }}>
            <h3 style={{ color: 'var(--accent-color)' }}>AI Explanation</h3>
            <p>{result.explanation}</p>
          </div>

          <button
            className="primary-btn"
            style={{ marginTop: '2rem', background: 'transparent', border: '2px solid white' }}
            onClick={() => {
              setResult(null)
              setPreview(null)
              setFile(null)
              setText('')
            }}
          >
            Start Over ↺
          </button>
        </div>
      )}
    </div>
  )
}

export default App
