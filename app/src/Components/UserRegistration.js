import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserRegistration.css';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await axios.post('http://127.0.0.1:5000/register', { username, password });
      alert('Registration successful: ' + data.message);
      fetchUsers(); // Fetch users after successful registration
    } catch (error) {
      alert('Registration failed: ' + error.response.data.error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/users');
      setUsers(response.data.users);
    } catch (error) {
      console.error("Couldn't fetch users", error);
    }
  };

  return (
    <div className="register-container">
      <form onSubmit={handleSubmit}>
        <h2>Register</h2>
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
        <button type="submit">Register</button>
      </form>
      
      {/* Display the list of users */}
      <div>
        <h2>Users</h2>
        <ul>
          {users.map((user) => (
            <li key={user.id}>
              Username: {user.username}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Register;
