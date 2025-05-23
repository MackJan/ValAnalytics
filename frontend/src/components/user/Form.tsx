import {useState} from "react";
import api from "../../api";
import {useNavigate} from "react-router-dom";
import {ACCESS_TOKEN, REFRESH_TOKEN} from "../../constants";
import "./Form.css";

interface FormProps {
    route: string;
    method: "login" | "register";
}

function Form({route, method}: FormProps) {
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);
            const res = await api.post(route, formData, {
                headers: {"Content-Type": "application/x-www-form-urlencoded"},
            });
            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                console.log(res.data.access);
                navigate("/dashboard");
            } else {
                console.log("User registered");
                navigate("/login");
            }
        } catch (error: unknown) {
            alert(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{name}</h1>
            <input
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            {loading}
            <button className="form-button" type="submit">
                {name}
            </button>
            <button
                className="form-button"
                type="button"
                onClick={() => navigate(method === "login" ? "/register" : "/login")}
            >
                {method === "login" ? "Register" : "Login"}
            </button>
        </form>
    );
}

export default Form;