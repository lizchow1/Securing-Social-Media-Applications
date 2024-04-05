import React, { useState } from 'react';
import GroupManagement from '../Components/GroupManagement';
import SecureMessaging from '../Components/SecureMessaging'; 
import './Home.css';

function Home({ userId }) {
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
