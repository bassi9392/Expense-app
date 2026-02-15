import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import API from '../services/api';

const Register = () => {
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await API.post('/auth/register', formData);
            alert("Registration successful! Please login.");
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.message || "Registration failed");
        }
    };

    return (
        <div style={containerStyle}>
            <h2>Create Account</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Username" required style={inputStyle}
                    onChange={(e) => setFormData({...formData, username: e.target.value})} />
                <input type="email" placeholder="Email" required style={inputStyle}
                    onChange={(e) => setFormData({...formData, email: e.target.value})} />
                <input type="password" placeholder="Password" required style={inputStyle}
                    onChange={(e) => setFormData({...formData, password: e.target.value})} />
                <button type="submit" style={btnStyle}>Register</button>
            </form>
            <p>Already have an account? <Link to="/login">Login</Link></p>
        </div>
    );
};

const containerStyle = { maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' };
const inputStyle = { display: 'block', width: '100%', padding: '10px', margin: '10px 0', boxSizing: 'border-box' };
const btnStyle = { width: '100%', padding: '10px', background: '#007bff', color: 'white', border: 'none', cursor: 'pointer' };

export default Register;