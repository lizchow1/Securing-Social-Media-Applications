import React from 'react';
import Group from'./Component/GroupManagement'
import Messaging from'./Component/SecureMessaging'

function Home() {
  return (
    <div>
      <Group/>
      <Messaging/>
    </div>
  );
}

export default Home;
