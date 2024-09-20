
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Admin from './components/Admin';
import Home from './components/Home';
import Teams from './components/Teams';
import HrTools from './components/HrTools'; // Import the HrTools component

function App() {
    const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || '');
    const [userName, setUserName] = useState(localStorage.getItem('userName') || '');
    const [userType, setUserType] = useState(localStorage.getItem('userType') || 'user');

    const saveAuthToken = (token, userName, userType) => {
        setAuthToken(token);
        setUserName(userName);
        setUserType(userType);
        localStorage.setItem('authToken', token);
        localStorage.setItem('userName', userName);
        localStorage.setItem('userType', userType);
    };

    const clearAuthToken = () => {
        setAuthToken('');
        setUserName('');
        setUserType('');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userName');
        localStorage.removeItem('userType');
    };

    return (
        <Router>
            <div>
                {/* Only show Navbar if the user is authenticated */}
                {authToken && <Navbar userName={userName} userType={userType} onLogout={clearAuthToken} />}

                <Routes>
                    {/* Default route goes to /login if not authenticated */}
                    <Route path="/" element={<Navigate to={authToken ? "/home" : "/login"} />} />
                    
                    {/* Login route */}
                    <Route path="/login" element={<Login setAuthToken={saveAuthToken} />} />
                    
                    {/* Protected routes */}
                    <Route path="/home" element={authToken ? <Home /> : <Navigate to="/login" />} />
                    <Route path="/admin" element={authToken && userType === 'superuser' ? <Admin authToken={authToken} /> : <Navigate to="/login" />} />
                    <Route path="/teams" element={authToken ? <Teams authToken={authToken} /> : <Navigate to="/login" />} />
                    <Route path="/hr-tools" element={authToken && userType === 'superuser' ? <HrTools authToken={authToken} userType={userType} /> : <Navigate to="/login" />} />
                    
                    {/* Catch-all redirects to login */}
                    <Route path="*" element={<Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
