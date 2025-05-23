import api from "./api";

const Home = () => {
  return (
    <div className="bg-[#201E1D] h-screen flex flex-col items-center justify-center">
       <button className="bg-zinc-700 hover:bg-zinc-900 text-white font-bold py-2 px-4 rounded"
        onClick={async () => {
          try {
            await api.get("/users/").then((response) => {
            console.log(response.data); // Handle the response data
              alert(JSON.stringify(response.data));
          })
          .catch((error) => {
            console.error("Error:", error); // Handle any errors
          });

          } catch (error) {
            alert("Error: " + error);
          }
        }}
      >
        Test API
      </button>
    </div>
  );
};

export default Home;
