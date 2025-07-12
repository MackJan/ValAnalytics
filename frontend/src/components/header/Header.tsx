import React from "react";

const Header: React.FC = () => {
    return (
        <header className="bg-indigo-400 text-white p-4 flex justify-between items-center">
            <h1>ValAnalytics</h1>
            <nav className="mx-auto flex max-w-7x1 items-center justify-between text-white">
                <ul className="flex space-x-4">
                    <li>
                        <a href="/" className="text-sm/6 font-semibold">Home</a>
                    </li>
                    <li>
                        <a href="/live" className="text-sm/6 font-semibold">Live</a>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;
