import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Clock, Calendar, Info, Menu, X, Download } from 'lucide-react';

const Sidebar: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        { icon: Home, label: 'Home', path: '/' },
        { icon: Clock, label: 'Live Matches', path: '/live' },
        { icon: Calendar, label: 'Match History', path: '/history' },
        { icon: Info, label: 'About', path: '/about' },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className={`bg-white border-r border-gray-200 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'} h-screen flex flex-col shadow-lg`}>
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                    {!isCollapsed && (
                        <h2 className="text-xl font-bold text-gray-800">Performance Tracker</h2>
                    )}
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        {isCollapsed ? <Menu size={20} /> : <X size={20} />}
                    </button>
                </div>
            </div>

            {/* Menu Items */}
            <div className="flex-1 py-4">
                <nav className="space-y-2 px-3">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const active = isActive(item.path);

                        return (
                            <button
                                key={item.path}
                                onClick={() => navigate(item.path)}
                                className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-200 group ${
                                    active 
                                        ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600' 
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                            >
                                <Icon size={20} className={`${active ? 'text-blue-600' : 'text-gray-500'} group-hover:text-gray-700`} />
                                {!isCollapsed && (
                                    <span className="font-medium">{item.label}</span>
                                )}
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* Download Agent Section */}
            <div className="p-4 border-t border-gray-200">
                <button className={`w-full flex items-center space-x-3 px-3 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors ${isCollapsed ? 'justify-center' : ''}`}>
                    <Download size={20} className="text-gray-600" />
                    {!isCollapsed && (
                        <span className="text-sm font-medium text-gray-700">Download Agent</span>
                    )}
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
