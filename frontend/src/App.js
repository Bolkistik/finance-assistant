import React, { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import AuthPage from './pages/AuthPage';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <AuthPage onLogin={handleLogin} />;
  }

  return (
    <>
      <button onClick={handleLogout} style={{
        position: 'absolute', top: 10, right: 10, zIndex: 1000
      }}>Выйти</button>
      <DashboardPage/>
    </>
  );
}

export default App;