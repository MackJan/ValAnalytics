import type {MenuData} from "./Dashboard.tsx";

const MenusDashboard: React.FC<{ menuData: MenuData }> = ({menuData}) => {
    return (
        <div className="min-h-screen bg-gray-900 text-white p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header Section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-purple-400 mb-2">Menu Dashboard</h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">In Party</h3>
                            <p className="truncate">{menuData.in_party ? "Yes" : "No"}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Rank</h3>
                            <p className={"font-semibold"}>
                                {menuData.rank}
                            </p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">RR</h3>
                            <p>{menuData.rr || "N/A"}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Leaderboard Ranking</h3>
                            <p>{menuData.leaderboard_rank || "N/A"}</p>
                        </div>
                    </div>
                </div>

                {/* Match Stats Section */}
                {/* Additional sections can be added here as needed */}
            </div>
        </div>
    );
}

export default MenusDashboard;