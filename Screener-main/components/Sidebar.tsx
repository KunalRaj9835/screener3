'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import {
  User,
  Briefcase,
  Hammer,
  Code,
  Copy,
  Settings,
  Trash2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const menuItems = [
    { icon: User, label: 'Profile', href: '/profile' },
    { icon: Briefcase, label: 'Portfolio', href: '/portfolio' },
    { icon: Hammer, label: 'Build', href: '/build', isActive: true },
    { icon: Code, label: 'Code', href: '/code' },
    { icon: Copy, label: 'Copy', href: '/copy' },
    { icon: Settings, label: 'Live tools', href: '/live-tools' },
    { icon: Trash2, label: 'Quest', href: '/quest' }
  ];

  return (
    <div className={`relative ${className}`}>
      {/* Sidebar */}
      <div 
        className={`
          bg-white h-screen transition-all duration-300 ease-in-out
          fixed left-0 top-0 z-[60]
          ${isCollapsed ? 'w-[5vw]' : 'w-[10vw]'}
        `}
      >
        {/* Header with Logo and Toggle */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className={`flex items-center transition-opacity duration-300 ${isCollapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100'}`}>
            <Image src="/logo.png" alt="TradeVed" width={100} height={50} />
          </div>
                    
          <button
            onClick={toggleSidebar}
            className="p-1 rounded-full hover:bg-gray-200 transition-colors duration-200 flex-shrink-0"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            )}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="mt-6">
          <ul className="space-y-2">
            {menuItems.map((item, index) => {
              const IconComponent = item.icon;
              return (
                <li key={index}>
                  <a
                    href={item.href}
                    className={`
                      flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 transition-colors duration-200
                      ${item.isActive ? ' bg-[#9bec00] text-white hover:bg-[#9bec00]' : ''}
                      ${isCollapsed ? 'justify-center' : ''}
                    `}
                  >
                    <IconComponent className={`w-5 h-5 ${isCollapsed ? '' : 'mr-3'}`} />
                    <span
                      className={`
                        transition-all duration-300
                        ${isCollapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100'}
                      `}
                    >
                      {item.label}
                    </span>
                  </a>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;