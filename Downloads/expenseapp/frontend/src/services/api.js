import axios from 'axios';

const API = axios.create({
    baseURL: 'http://localhost:5000/api'
});

// This "Interceptor" grabs the token from your browser's local storage
// and attaches it to the 'Authorization' header automatically.
API.interceptors.request.use((req) => {
    const token = localStorage.getItem('token');
    if (token) {
        req.headers.Authorization = `Bearer ${token}`;
    }
    return req;
});

export default API;