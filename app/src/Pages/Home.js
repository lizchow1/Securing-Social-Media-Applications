import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import GroupManagement from '../Components/GroupManagement';
import SecureMessaging from '../Components/SecureMessaging'; 
import axios from 'axios';
import './Home.css';

function Home() {
  const location = useLocation();
  const userId = location.state?.userId; // Access userId from navigation state
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [messages, setMessages] = useState([]);

  const fetchMessages = async (groupId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/view_message_in_group`, {
        params: { group_id: groupId, user_id: userId }
      });
      setMessages(response.data.messages);
    } catch (error) {
      console.error("Couldn't fetch messages for group", error);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const handleSelectGroup = (group) => {
    setSelectedGroup(group);
    fetchMessages(group.id);
  };

  return (
    <div className='home-container'>
      <GroupManagement userId={userId} onSelectGroup={handleSelectGroup} onLeaveGroup={clearMessages} />
      <SecureMessaging selectedGroup={selectedGroup} userId={userId} messages={messages} onMessagesUpdate={fetchMessages} />
    </div>
  );
}

export default Home;
