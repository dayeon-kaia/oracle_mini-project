// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

import { useEffect, useState } from "react";
import api from "./services/api";
import "./App.css";

function App() {
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/patients")
      .then((res) => {
        console.log("API 응답:", res.data);
        setPatients(res.data.data);
      })
      .catch((err) => {
        console.error("API 에러:", err);
        setError(err.message);
      });
  }, []);

  return (
    <div>
      <h1>CORS 테스트</h1>
      {error && <p style={{ color: "red" }}>❌ 에러: {error}</p>}
      {patients.length > 0 && (
        <div>
          <p>API 연결 성공!</p>
          <pre>{JSON.stringify(patients, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
