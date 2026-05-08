import React, { useState } from 'react';
import { register, login } from '../services/api';

function AuthPage({ onLogin }) {
    const [isLogin, setisLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            let response;
            if (isLogin) {
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);
                response = await login(formData);
            } else {
                response = await register({ email, password });
            }

            const token = response.data.access_token;
            localStorage.setItem('token', token);
            onLogin(token);
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка. Проверьте данные');
        }
    };

    return (
        <div style={{
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            minHeight: '100vh', background: '#f0f2f5', fontFamily: 'Arial'
        }}>
            <div style={{
                background: '#fff', padding: 40, borderRadius: 16,
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)', width: 400
            }}>
                <h2 style={{ textAlign: 'center', marginBottom:30 }}>
                    {isLogin ? 'Вход' : 'Регистрация'}
                </h2>

                {error && (
                    <div style={{
                        background: '#ffebee', color: '#c62828',
                        padding: 12, borderRadius: 8, marginBottom: 20
                    }}>{error}</div>
                )}

                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        required
                        style={{
                            width: '100%', padding: 12, fontSize: 16,
                            border: '1px solid #ddd', borderRadius: 8,
                            marginBottom: 15, boxSizing: 'border-box'
                        }}
                    />

                    <input
                        type="password"
                        placeholder="Пароль"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                        style={{
                            width: '100%', padding: 12, fontSize: 16,
                            border: '1px solid #ddd', borderRadius: 8,
                            marginBottom: 20, boxSizing: 'border-box'
                        }}
                    />

                    <button type="submit" style={{
                        width: '100%', padding: 12, fontSize: 16,
                        background: '#1976d2', color: '#fff', borderRadius: 8, cursor: 'pointer', fontWeight: 'bold'
                    }}>
                        {isLogin ? 'Войти' : 'Зарегистрироваться'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 20, color: '#666'}}>
                    {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
                    <span onClick={() => setisLogin(!isLogin)} style ={{
                        color: '#1976d2', cursor: 'pointer', textDecoration: 'underline'
                    }}>
                        {isLogin ? 'Регистрация' : 'Войти'}
                    </span>
                </p>
            </div>
        </div>
    );
}

export default AuthPage;