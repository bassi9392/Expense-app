import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// 1. Create the Context (The "Brain")
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    // State to store user data
    const [user, setUser] = useState(null);
    // State to handle the "loading" phase while we check the browser storage
    const [loading, setLoading] = useState(true);
    
    const navigate = useNavigate();

    // 2. Check for an existing session on startup
    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        if (storedUser && token) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    // 3. Login Function
    const login = (userData, token) => {
        // Save to browser memory so session persists on refresh
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Update the state
        setUser(userData);
        
        // Redirect to Dashboard
        navigate('/dashboard');
    };

    // 4. Logout Function
    const logout = () => {
        // Clear browser memory
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Reset state
        setUser(null);
        
        // Send user back to Login page
        navigate('/login');
    };

    // 5. Provide everything to the App
    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};