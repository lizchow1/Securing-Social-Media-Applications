import UserRegistration from '../Components/UserRegistration';
import Login from '../Components/Login';
import './SignIn.css';

function SignIn() {

    return (
        <div className="signin-container">
            <UserRegistration/>
            <Login />
        </div>
    );
}

export default SignIn;