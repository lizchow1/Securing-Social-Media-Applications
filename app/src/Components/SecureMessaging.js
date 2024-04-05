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
      const response = await axios.get(`http://127.0.0.1:5000/groups/${groupId}/messages`);
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

  if (!selectedGroup) {
    return <p>Select a group to view messages.</p>;
  }

  return (
    <div>
      <h2>Messages in {selectedGroup.group_name}</h2>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg.content}</li>
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
      </form>
    </div>
  );
}

export default SecureMessaging;
