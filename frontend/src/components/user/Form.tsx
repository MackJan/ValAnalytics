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
        <div className="h-screen bg-[#201E1D] flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                <img
                    alt="Your Company"
                    src="/logo.jpg"
                    className="mx-auto h-10 w-auto"
                />
                <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-neutral-50">
                    ValorAnalytics {name}
                </h2>
            </div>

            <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                <form onSubmit={handleSubmit} className="form-container">
                    <h1 className="text-neutral-50">{name}</h1>
                    <div>
                        <label htmlFor="email" className="block text-sm/6 font-medium text-neutral-50">
                            Email address
                        </label>
                        <div className="mt-2">
                            <input
                                className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                id="username"
                                name="username"
                                autoComplete="username"
                                required
                                placeholder="Username"
                            />
                        </div>
                    </div>
                    <div>
                        <div className="flex items-center justify-between">
                            <label htmlFor="password" className="block text-sm/6 font-medium text-neutral-50">
                                Password
                            </label>
                        </div>
                        <div className="mt-2">
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Password"
                            />
                        </div>
                    </div>
                    {loading}
                    <div>
                        <button
                            className="flex justify-center rounded-md bg-[#EBF5EE] px-3 py-1.5 text-sm/6 font-semibold text-black shadow-xs hover:bg-[#7B6D8D] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            type="submit">
                            {name}
                        </button>
                        <button
                            className="flex justify-center rounded-md bg-[#EBF5EE] px-3 py-1.5 text-sm/6 font-semibold text-black shadow-xs hover:bg-[#7B6D8D] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            type="submit"
                            onClick={() => navigate(method === "login" ? "/register" : "/login")}
                        >
                            {method === "login" ? "Register" : "Login"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Form;