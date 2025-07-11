import React from 'react';
import type {MenuData} from "./Dashboard.tsx";

const MenusDashboard: React.FC<{ menuData: MenuData }> = ({menuData}) => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header Section */}
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                                Menu Dashboard
                            </h1>
                            <p className="text-gray-400">Player status and information</p>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-400">Live</span>
                        </div>
                    </div>

                    {/* Main Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl hover:bg-slate-800/80 transition-all duration-200">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Player Name</h3>
                                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                            </div>
                            <p className="text-xl font-bold text-white truncate">{menuData.name}</p>
                        </div>

                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl hover:bg-slate-800/80 transition-all duration-200">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Current Rank</h3>
                                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                            </div>
                            <p className="text-xl font-bold text-white">{menuData.rank}</p>
                        </div>

                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl hover:bg-slate-800/80 transition-all duration-200">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">RR Points</h3>
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            </div>
                            <p className="text-xl font-bold text-white">{menuData.rr || "N/A"}</p>
                        </div>

                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl hover:bg-slate-800/80 transition-all duration-200">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Party Status</h3>
                                <div className={`w-2 h-2 rounded-full ${menuData.in_party ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                            </div>
                            <p className="text-xl font-bold text-white">{menuData.in_party ? "In Party" : "Solo"}</p>
                        </div>
                    </div>

                    {/* Additional Info Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl">
                            <h3 className="text-lg font-semibold text-white mb-4">Leaderboard Information</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-400">Leaderboard Rank</span>
                                    <span className="text-white font-medium">{menuData.leaderboard_rank || "Unranked"}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-400">Season</span>
                                    <span className="text-white font-medium">{menuData.season || "Current"}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700 p-6 rounded-xl">
                            <h3 className="text-lg font-semibold text-white mb-4">Status Overview</h3>
                            <div className="space-y-3">
                                <div className="flex items-center space-x-3">
                                    <div className={`w-3 h-3 rounded-full ${menuData.in_party ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                                    <span className="text-gray-400">
                                        {menuData.in_party ? "Currently in party" : "Playing solo"}
                                    </span>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                                    <span className="text-gray-400">Menu active</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default MenusDashboard;