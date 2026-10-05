import React, { useState } from 'react';

const navItems = [
  { name: 'Home', href: '/' },
  { name: 'Plants', href: '/plants' },
  { name: 'RIP', href: '/plants/rip' },
  { name: 'Profile', href: '/profile' },
];  

function NavIsland() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div>
      <h2>Navigation Island</h2>
      <nav>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/plants">Plants</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </nav>
    </div>
  )
}

export default NavIsland