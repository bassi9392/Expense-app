import React, { useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import API from '../services/api';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useContext(AuthContext);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await API.post('/auth/login', { email, password });
            login(res.data.user, res.data.token);
        } catch (err) {
            setError("Invalid credentials");
        }
    };

    return (
        <div style={containerStyle}>
            <h2>Login</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <input type="email" placeholder="Email" required style={inputStyle} onChange={(e) => setEmail(e.target.value)} />
                <input type="password" placeholder="Password" required style={inputStyle} onChange={(e) => setPassword(e.target.value)} />
                <button type="submit" style={{ ...btnStyle, background: '#28a745' }}>Login</button>
            </form>
            <p>New user? <Link to="/register">Create account</Link></p>
        </div>
    );
};

// Reusing styles from Register.js
const containerStyle = { maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' };
const inputStyle = { display: 'block', width: '100%', padding: '10px', margin: '10px 0', boxSizing: 'border-box' };
const btnStyle = { width: '100%', padding: '10px', color: 'white', border: 'none', cursor: 'pointer' };

export default Login;