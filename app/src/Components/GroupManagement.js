import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GroupManagement.css';

function GroupManagement({ userId, onSelectGroup, onLeaveGroup }) {
  const [groups, setGroups] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [username, setUsername] = useState('');

  useEffect(() => {
    fetchGroups();
    fetchUserDetails();  
  }, []);

  const fetchUserDetails = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/get_username`, { params: { user_id: userId } });
      setUsername(response.data.username);  
    } catch (error) {
      console.error("Couldn't fetch user details", error);
    }
  };

  const fetchGroups = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/groups');
      setGroups(response.data.groups);
    } catch (error) {
      console.error("Couldn't fetch groups", error);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:5000/create_group', { group_name: groupName });
      fetchGroups(); 
      setGroupName(''); 
    } catch (error) {
      console.error("Couldn't create group", error);
    }
  };

  const handleSelectGroup = (group) => {
    setSelectedGroup(group);
  };

  const handleJoinGroup = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/add_user', { group_id: selectedGroup.id, user_id: userId });
      onSelectGroup(selectedGroup); // Pass the selected group up to parent component to fetch messages
    } catch (error) {
      console.error("Couldn't join group", error);
    }
  };

  const handleLeaveGroup = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/remove_user', {
        group_id: selectedGroup.id,
        user_id: userId
      });
      onLeaveGroup(); // Call the passed down function to clear messages
      setSelectedGroup(null); // Clear the selected group
    } catch (error) {
      console.error("Couldn't leave group", error);
    }
  };

  const handleViewMessages = () => {
    if (selectedGroup) {
      onSelectGroup(selectedGroup);
    }
  };

  return (
    <div className="group-container">
      <h2>Group Management</h2>
      <p>Welcome, {username}!</p>
      <form onSubmit={handleCreateGroup}>
        <input
          type="text"
          placeholder="Group Name"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />
        <button type="submit">Create Group</button>
      </form>
      <h3>Groups</h3>
      <ul>
        {groups.map((group) => (
          <li
            key={group.id}
            onClick={() => handleSelectGroup(group)}
            className={selectedGroup && group.id === selectedGroup.id ? 'selected' : ''}>
            {group.group_name}
          </li>
        ))}
      </ul>

      {selectedGroup && (
        <div>
          <h3>Selected Group: {selectedGroup.group_name}</h3>
          <button onClick={handleJoinGroup}>Join Group</button>
          <button onClick={handleLeaveGroup}>Leave Group</button>
          <button onClick={handleViewMessages}>View Messages</button>
        </div>
      )}
    </div>
  );
}

export default GroupManagement;
