import React, { useState, useEffect } from 'react';
import axios from 'axios';

function GroupManagement() {
  const [groups, setGroups] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);

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
      await axios.post('http://127.0.0.1:5000/create_group', { name: groupName });
      fetchGroups();
      setGroupName('');
    } catch (error) {
      console.error("Couldn't create group", error);
    }
  };

  return (
    <div>
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
          <li key={group.id} onClick={() => setSelectedGroup(group)}>
            {group.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default GroupManagement;
