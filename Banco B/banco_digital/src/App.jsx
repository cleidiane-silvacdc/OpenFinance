import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:5000'

export default function App() {
  const [view, setView] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [userData, setUserData] = useState(null)
  
  const [loginData, setLoginData] = useState({ cpf: '', senha: '' })
  const [cadastroData, setCadastroData] = useState({
    nome: '',
    cpf: '',
    idade: '',
    renda: '',
    tempo_emprego: '',
    tipo_emprego: '',
    senha: ''
  })

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setUserData(data)
        setView('dashboard')
        setLoginData({ cpf: '', senha: '' })
      } else {
        setError(data.erro || 'Erro no login')
      }
    } catch (err) {
      setError('Erro de conexão com servidor: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCadastro = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/cadastro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...cadastroData,
          idade: parseInt(cadastroData.idade),
          renda: parseFloat(cadastroData.renda)
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setError('Conta criada com sucesso! Faça login.')
        setCadastroData({
          nome: '',
          cpf: '',
          idade: '',
          renda: '',
          tempo_emprego: '',
          tipo_emprego: '',
          senha: ''
        })
        setTimeout(() => setView('login'), 2000)
      } else {
        setError(data.erro || 'Erro no cadastro')
      }
    } catch (err) {
      setError('Erro de conexão com servidor: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>Banco Digital</h1>
      </header>
      
      <main className="main-content">
        {view === 'login' && (
          <div className="form-container">
            <h2>Login</h2>
            {error && <div className="error">{error}</div>}
            <form onSubmit={handleLogin}>
              <input 
                type="text" 
                placeholder="CPF" 
                value={loginData.cpf}
                onChange={(e) => setLoginData({...loginData, cpf: e.target.value})}
                disabled={loading}
              />
              <input 
                type="password" 
                placeholder="Senha"
                value={loginData.senha}
                onChange={(e) => setLoginData({...loginData, senha: e.target.value})}
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Entrando...' : 'Entrar'}
              </button>
            </form>
            <p>Não tem conta? <button className="link-btn" onClick={() => setView('cadastro')}>Cadastre-se</button></p>
          </div>
        )}

        {view === 'cadastro' && (
          <div className="form-container">
            <h2>Cadastro</h2>
            {error && <div className="error">{error}</div>}
            <form onSubmit={handleCadastro}>
              <input 
                type="text" 
                placeholder="Nome completo"
                value={cadastroData.nome}
                onChange={(e) => setCadastroData({...cadastroData, nome: e.target.value})}
                disabled={loading}
              />
              <input 
                type="text" 
                placeholder="CPF"
                value={cadastroData.cpf}
                onChange={(e) => setCadastroData({...cadastroData, cpf: e.target.value})}
                disabled={loading}
              />
              <input 
                type="text" 
                placeholder="Idade"
                value={cadastroData.idade}
                onChange={(e) => setCadastroData({...cadastroData, idade: e.target.value})}
                disabled={loading}
              />
              <input 
                type="text" 
                placeholder="Renda"
                value={cadastroData.renda}
                onChange={(e) => setCadastroData({...cadastroData, renda: e.target.value})}
                disabled={loading}
              />
              <input 
                type="text" 
                placeholder="Tempo de emprego"
                value={cadastroData.tempo_emprego}
                onChange={(e) => setCadastroData({...cadastroData, tempo_emprego: e.target.value})}
                disabled={loading}
              />
              <input 
                type="text" 
                placeholder="Tipo de emprego"
                value={cadastroData.tipo_emprego}
                onChange={(e) => setCadastroData({...cadastroData, tipo_emprego: e.target.value})}
                disabled={loading}
              />
              <input 
                type="password" 
                placeholder="Senha"
                value={cadastroData.senha}
                onChange={(e) => setCadastroData({...cadastroData, senha: e.target.value})}
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Cadastrando...' : 'Cadastrar'}
              </button>
            </form>
            <p><button className="link-btn" onClick={() => setView('login')}>Voltar ao login</button></p>
          </div>
        )}

        {view === 'dashboard' && userData && (
          <div className="dashboard-container">
            <h2>Bem-vindo, {userData.nome}!</h2>
            <div className="account-info">
              <p><strong>CPF:</strong> {userData.cpf}</p>
              <p><strong>Saldo:</strong> R$ {userData.saldo?.toFixed(2) || '0.00'}</p>
              <p><strong>Limite de Crédito:</strong> R$ {userData.limite_credito?.toFixed(2) || '0.00'}</p>
              <p><strong>Score:</strong> {userData.score}</p>
              <p><strong>Agência:</strong> {userData.agencia}</p>
              <p><strong>Conta:</strong> {userData.conta}</p>
            </div>
            <button className="logout-btn" onClick={() => {
              setUserData(null)
              setView('login')
              setError('')
            }}>Sair</button>
          </div>
        )}
      </main>
    </div>
  )
}
