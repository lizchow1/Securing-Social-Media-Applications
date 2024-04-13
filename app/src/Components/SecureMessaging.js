import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SecureMessaging.css';

function SecureMessaging({ selectedGroup, userId }) { // Accept userId as prop
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (selectedGroup) {
      fetchMessages(selectedGroup.id);
    }
  }, [selectedGroup]);

  const fetchMessages = async (groupId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/view_message_in_group`, {
        params: { group_id: selectedGroup.id, user_id: userId }
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
      const response = await axios.post(`http://127.0.0.1:5000/send_message_to_group`, {
        user_id: userId,
        group_id: selectedGroup.id,
        message: newMessage
      });
      if (response.data.error) {
        setErrorMessage(response.data.error);
      } else {
        setNewMessage('');
        fetchMessages(selectedGroup.id);
        setErrorMessage(''); 
      }
    } catch (error) {
      console.error("Couldn't send message", error);
      setErrorMessage("Unable to send message. Please try again later.");
    }
  };

  if (!selectedGroup) {
    return <p>Select a group to view messages.</p>;
  }

  return (
  <div className="message-board">
    <h2>Messages in {selectedGroup.group_name}</h2>
    <ul className="message-list">
      {messages.map((msg, index) => (
        <li key={index} className="message-item">
          <div className="message-author">{userId}</div>
          <div className="message-content">
            {msg.encrypted ? "Encrypted Message" : msg.content}
          </div>
          <div className="message-timestamp">4 years ago {/* Replace with actual timestamp if available */}</div>
        </li>
      ))}
    </ul>
    <form onSubmit={handleSendMessage} className="message-form">
      <input
        className="message-input"
        type="text"
        placeholder="Your message*"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
      />
      <button type="submit" className="send-button">Send</button>
    </form>
    {errorMessage && <div className="error-message">{errorMessage}</div>}
  </div>

  );
}

export default SecureMessaging;
