import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import GroupManagement from '../Components/GroupManagement';
import SecureMessaging from '../Components/SecureMessaging'; 
import './Home.css';

function Home() { 
    const location = useLocation();
    const userId = location.state?.userId; // Access userId from navigation state
    const [selectedGroup, setSelectedGroup] = useState(null);

    // Define onSelectGroup function
    const handleSelectGroup = (group) => {
        setSelectedGroup(group);
    };

    return (
        <div className='home-container'>
            {/* Pass onSelectGroup function as a prop */}
            <GroupManagement onSelectGroup={handleSelectGroup} />
            <SecureMessaging selectedGroup={selectedGroup} userId={userId} />
        </div>
    );
}

export default Home;
