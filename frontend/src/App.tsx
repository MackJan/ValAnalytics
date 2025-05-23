import './App.css';
import Login from "./components/user/Login.tsx";
import Register from "./components/user/Register.tsx";
import Home from "./Home";
import Header from "./components/header/Header.tsx";
import RiotLogin from "./components/riot_user/Login.tsx";

import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";
import Tracker from "./components/Tracker";

const App = () => {
    return (
        <Router>
            <Header/>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/tracker" element={<Tracker />} />
                <Route path="/login" element={<Login/>} />
                <Route path="/register" element={<Register/>} />
                <Route path="/riot_login" element={<RiotLogin/>} />
            </Routes>
        </Router>
    );
};

export default App;