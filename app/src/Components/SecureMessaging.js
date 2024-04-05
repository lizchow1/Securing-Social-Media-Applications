import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SecureMessaging({ selectedGroup, userId }) { // Accept userId as prop
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    if (selectedGroup) {
      fetchMessages(selectedGroup.id);
    }
  }, [selectedGroup]);

  const fetchMessages = async (groupId) => {
    try {
      console.log("Fetching messages for user ID:", userId); // Add this line
      const response = await axios.get(`http://127.0.0.1:5000/groups/${groupId}/messages`, {
        params: { user_id: userId }
      });
      setMessages(response.data.messages);
    } catch (error) {
      console.error("Couldn't fetch messages", error);
    }
  };
  

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!selectedGroup) return;
    try {
      await axios.post(`http://127.0.0.1:5000/send_message_to_group`, {
        user_id: userId, // Pass userId as part of the request body
        group_id: selectedGroup.id,
        message: newMessage
      });
      setNewMessage('');
      fetchMessages(selectedGroup.id);
    } catch (error) {
      console.error("Couldn't send message", error);
    }
  };

  const handleViewMessages = async () => {
    if (!selectedGroup) return;
    try {
      const response = await axios.get('http://127.0.0.1:5000/view_message_in_group', {
        params: { user_id: userId, group_id: selectedGroup.id }
      });
      console.log(response.data.messages)
      setMessages(response.data.messages); // Update state with the new messages
    } catch (error) {
      console.error("Couldn't view messages", error);
    }
  };

  if (!selectedGroup) {
    return <p>Select a group to view messages.</p>;
  }

  return (
    <div>
      <h2>Messages in {selectedGroup.group_name}</h2>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>
            {msg.encrypted ? "Encrypted Message" : msg.content}
          </li>
        ))}
      </ul>
      <form onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Write a message"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <button type="submit">Send</button>
        <button onClick={handleViewMessages}>View Messages</button> 
      </form>
    </div>
  );
}

export default SecureMessaging;
