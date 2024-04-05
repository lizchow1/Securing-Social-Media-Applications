import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; 
import './Login.css';

function Login({ setUserId }) { // Accept setUser prop to update user state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate(); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/login', { username, password });
      if (response) {
        alert('Login successful');
        // Set user state with user_id
        setUserId(response.data.userId);
        // Redirect to the home page upon successful login
        navigate('/home'); 
      } 
    } catch (error) {
      setError('Login failed: ' + error.response?.data?.error || 'Unknown error');
    }
  };

  return (
    <div className="login-container">
        <form onSubmit={handleSubmit}>
          <h2>Login</h2>
          <div>
            <label>Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit">Login</button>
        </form>
    </div>
  );
}

export default Login;
