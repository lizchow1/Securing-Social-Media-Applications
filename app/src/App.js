import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'; // Import Routes

import Home from './Pages/Home';
import SignIn from './Pages/SignIn';

function App() {
  return (
    <Router>
      <div>
        {/* Navigation links for easy navigation
        <nav>
          <ul>
            <li>
              <Link to="/home">Home</Link>
            </li>
            <li>
              <Link to="/signin">Sign In</Link>
            </li>
          </ul>
        </nav> */}

        {/* Route configuration */}
        <Routes> {/* Wrap your Routes with the <Routes> component */}
          <Route path="/signin" element={<SignIn />} /> {/* Use element prop to specify the component */}
          <Route path="/home" element={<Home />} /> {/* Use element prop to specify the component */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
