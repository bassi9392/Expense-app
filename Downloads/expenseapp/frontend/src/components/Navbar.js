import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useContext(AuthContext);

    return (
        <nav style={navStyle}>
            <div style={{ fontWeight: 'bold', fontSize: '20px' }}>
                <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Bellcorp Tracker</Link>
            </div>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                {user ? (
                    <>
                        <Link to="/dashboard" style={linkStyle}>Dashboard</Link>
                        <Link to="/explorer" style={linkStyle}>Explorer</Link>
                        <span style={{ color: '#00d1b2' }}>Hi, {user.username}</span>
                        <button onClick={logout} style={logoutBtn}>Logout</button>
                    </>
                ) : (
                    <>
                        <Link to="/login" style={linkStyle}>Login</Link>
                        <Link to="/register" style={linkStyle}>Register</Link>
                    </>
                )}
            </div>
        </nav>
    );
};

const navStyle = { display: 'flex', justifyContent: 'space-between', padding: '1rem 2rem', background: '#2c3e50', color: 'white' };
const linkStyle = { color: 'white', textDecoration: 'none' };
const logoutBtn = { background: '#ff4757', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' };

export default Navbar;