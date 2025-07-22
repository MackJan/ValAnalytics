const Home = () => {
    return (
        <div className="bg-gray-100 h-screen flex flex-col items-center justify-center text-black">
            <h1 className="text-4xl font-bold mb-4">Welcome to Performance Tracker</h1>
            <p className="text-lg mb-6 text-center max-w-md">
                Performance Tracker helps you monitor and analyze your activities to improve efficiency and achieve your
                goals. Explore the features and start tracking today!
            </p>
            <p className="text-lg mb-6 text-center max-w-md">Currently woking features include:</p>
            <ul className="list-disc list-inside mb-6 text-center max-w-md">
                <li>Live Matches
                    <p>filled with dummy data</p>
                </li>
            </ul>
        </div>
    );
};

export default Home;
