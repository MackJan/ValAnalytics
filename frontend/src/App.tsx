import './App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";
import Tracker from "./components/Tracker";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<div>Home</div>} />
                <Route path="/tracker" element={<Tracker />} />
            </Routes>
        </Router>
    );
};

export default App;