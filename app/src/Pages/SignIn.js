import React, { useState } from 'react';
import UserRegistration from '../Components/UserRegistration';
import Login from '../Components/Login';
import './SignIn.css';

function SignIn() {
    const [userId, setUserId] = useState(null);

    return (
        <div className="signin-container">
            <UserRegistration/>
            <Login setUserId={setUserId} />
        </div>
    );
}

export default SignIn;