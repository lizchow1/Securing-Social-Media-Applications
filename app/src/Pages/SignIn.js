import React from "react";
import UserRegistration from'./Component/UserRegistration'
import Login from'./Component/Login'

function SignIn(){
    return(
        <div className="SignIn-container">
            <UserRegistration/>
            <Login/>
        </div>
    )
}

export default SignIn;