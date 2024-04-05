import React from "react";
import UserRegistration from'../Components/UserRegistration'
import Login from'../Components/Login'

function SignIn(){
    return(
        <div className="SignIn-container">
            <UserRegistration/>
            <Login/>
        </div>
    )
}

export default SignIn;