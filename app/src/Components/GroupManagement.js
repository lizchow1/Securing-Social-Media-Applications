import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GroupManagement.css';

function GroupManagement({ onSelectGroup }) {
  const [groups, setGroups] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [username, setUsername] = useState(''); // Change to username
  const [usersInGroup, setUsersInGroup] = useState([]);
  const [userId, setUserId] = useState(null); // Declare userId state variable

  useEffect(() => {
    fetchGroups();
  }, []);

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
      fetchGroups(); // Refresh groups after creating a new one
      setGroupName(''); // Clear input field
    } catch (error) {
      console.error("Couldn't create group", error);
    }
  };

  const handleSelectGroup = (group) => {
    setSelectedGroup(group);
    fetchUsersInGroup(group.id);
    onSelectGroup(group);
};

  const fetchUsersInGroup = async (groupId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/groups/${groupId}/users`);
      setUsersInGroup(response.data.users);
    } catch (error) {
      console.error("Couldn't fetch users in group", error);
    }
  };

  const handleAddUserToGroup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`http://127.0.0.1:5000/get_user_id?username=${username}`);
      if(response){
        const userData = response.data;
        const userId = userData.user_id; // Get userId from response
        await axios.post('http://127.0.0.1:5000/add_user', { group_id: selectedGroup.id, user_id: userId });
        // Refresh users in group after adding user
        fetchUsersInGroup(selectedGroup.id);
      }
    } catch (error) {
      console.error("Couldn't add user to group", error);
    }
  };
  

  const handleRemoveUserFromGroup = async (userId) => {
    try {
      await axios.post('http://127.0.0.1:5000/remove_user', { group_id: selectedGroup.id, user_id: userId });
      // Refresh users in group after removing user
      fetchUsersInGroup(selectedGroup.id);
    } catch (error) {
      console.error("Couldn't remove user from group", error);
    }
  };

  return (
    <div className="group-container">
      <h2>Group Management</h2>
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
          <li key={group.id} onClick={() => handleSelectGroup(group)}>
            {group.group_name}
          </li>
        ))}
      </ul>
      {selectedGroup && (
        <div>
          <h3>Selected Group: {selectedGroup.group_name}</h3>
          <p>ID: {selectedGroup.id}</p>
          {/* Display users in the group */}
          <h3>Users in Group</h3>
          <ul>
            {usersInGroup.map((user) => (
              <li key={user.id}>
                {user.username}
                <button onClick={() => handleRemoveUserFromGroup(user.id)}>Remove</button>
              </li>
            ))}
          </ul>
          {/* Form to add user */}
          <form onSubmit={handleAddUserToGroup}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <button type="submit">Add User</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default GroupManagement;
