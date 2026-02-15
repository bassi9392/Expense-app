import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Providers & Components
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Explorer from './pages/Explorer';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        {/* The Navbar stays at the top of all pages */}
        <Navbar />

        {/* Main Content Area */}
        <div className="container">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes (Require Login) */}
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/explorer" 
              element={
                <PrivateRoute>
                  <Explorer />
                </PrivateRoute>
              } 
            />

            {/* Redirects */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </div>
    </AuthProvider>
  );
}

export default App;