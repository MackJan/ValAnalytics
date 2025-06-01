import type {MenuData} from "./Dashboard.tsx";

const MenusDashboard: React.FC<{ manuData: MenuData }> = ({menuData}) => {
    const {menu} = menuData;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header Section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-purple-400 mb-2">Menu Dashboard</h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">In Party</h3>
                            <p className="truncate">{menu.InParty}</p>
                            {menu.InParty && (
                                <p className="text-sm text-gray-500">{menu.PartySize}/5</p>)}
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Rank</h3>
                            <p className={"font-semibold"}>
                                {menu.Rank}
                            </p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">RR</h3>
                            <p>{menu.RR}</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h3 className="text-sm text-gray-400">Leaderboard Ranking</h3>
                            <p>{menu.LeaderboardRank}</p>
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