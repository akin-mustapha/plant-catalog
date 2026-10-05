import React, { useState } from 'react';
import { Home, PlantPot, Cross, CircleUserRound } from 'lucide-react';

const navItems = [
  { id: 'Home', href: '/', label: 'Home', icon: Home },
  { id: 'Plants', href: '/plants', icon: PlantPot },
  { id: 'RIP', href: '/plants/rip', icon: Cross },
  { id: 'Profile', href: '/profile', icon: CircleUserRound },
];  

function NavIsland() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <nav>
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;

        return <>
          <button>
            <Icon />

          </button>
        </>
      })}


    </nav>
  )
}

export default NavIsland