import api from "./api";

const Home = () => {
  return (
    <div>
       <button
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
