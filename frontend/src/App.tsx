import './App.css';
import Home from "./Home";
import Header from "./components/header/Header.tsx";
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
            <Header/>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/live" element={<ActiveMatches/>}/>
                <Route
                    path="/live/:matchUuid"
                    element={<LiveDashboard/>}
                />
            </Routes>
        </Router>
    );
};

export default App;