import './App.css';
import Home from "./Home";
import Sidebar from "./components/sidebar/Sidebar.tsx";
import {LiveDashboard} from "./components/match_dashboard/Dashboard.tsx";
import ActiveMatches from "./components/match_dashboard/ActiveMatches.tsx";

import {
    BrowserRouter as Router,
    Routes,
    Route,
} from "react-router-dom";

const App = () => {
    return (
        <Router>
            <div className="flex h-screen bg-gray-50">
                <Sidebar />
                <div className="flex-1 overflow-auto">
                    <Routes>
                        <Route path="/" element={<Home/>}/>
                        <Route path="/live" element={<ActiveMatches/>}/>
                        <Route
                            path="/live/:matchUuid"
                            element={<LiveDashboard/>}
                        />
                    </Routes>
                </div>
            </div>
        </Router>
    );
};

export default App;