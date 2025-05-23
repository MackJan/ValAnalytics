import HCaptcha from '@hcaptcha/react-hcaptcha';
import {useState, useRef, useEffect} from "react";
import api from "../../api.ts";


function RiotLogin() {
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [token, setToken] = useState(null);
    const captchaRef = useRef(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);
            formData.append("hcaptcha_token", token || ""); // Ensure token is not null
            console.log("Request Payload:", formData.toString());
            const res = await api.post("/auth/riot/", formData, {
                headers: {"Content-Type": "application/x-www-form-urlencoded"},
            });
            console.log("Response:", res);
        } catch (error: unknown) {
            console.error("Error:", error);
            alert("An error occurred. Check the console for details.");
        } finally {
            setLoading(false);
        }
    };

    const onLoad = () => {
        // this reaches out to the hCaptcha JS API and runs the
        // execute function on it. you can use other functions as
        // documented here:
        // https://docs.hcaptcha.com/configuration#jsapi
        captchaRef.current.execute();
    };
    useEffect(() => {

        if (token)
            console.log(`hCaptcha Token: ${token}`);

    }, [token]);

    return (
        <div className="h-screen bg-[#201E1D] flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                <img
                    alt="Your Company"
                    src="/logo.jpg"
                    className="mx-auto h-10 w-auto"
                />
                <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-neutral-50">
                    ValorAnalytics
                </h2>
            </div>

            <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                <form onSubmit={handleSubmit} className="form-container">
                    <h1 className="text-neutral-50">Riot Login</h1>
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
                    <form>
                        <HCaptcha
                            sitekey="80e8c4b0-2226-4a1a-a57e-2cd86088fb04"
                            onLoad={onLoad}
                            onVerify={(token) => {
                                setToken(token);
                            }}
                            ref={captchaRef}
                        />
                    </form>
                    <div>
                        <button
                            className="flex justify-center rounded-md bg-[#EBF5EE] px-3 py-1.5 text-sm/6 font-semibold text-black shadow-xs hover:bg-[#7B6D8D] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            type="submit">
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default RiotLogin;