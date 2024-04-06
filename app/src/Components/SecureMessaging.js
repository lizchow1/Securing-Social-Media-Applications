import React, { useState, useEffect } from 'react';
import axios from 'axios';

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
        setErrorMessage(''); // Clear any previous error message
      }
    } catch (error) {
      console.error("Couldn't send message", error);
      setErrorMessage("Unable to send message. Please try again later.");
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
      </form>
      <button onClick={handleViewMessages}>View Messages</button> 
      {errorMessage && <div className="error-message">{errorMessage}</div>}
    </div>
  );
}

export default SecureMessaging;
