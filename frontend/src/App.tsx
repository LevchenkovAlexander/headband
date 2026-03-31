import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainPage from "./components/MainPage/MainPage";
import Schedule from "./components/Schedule/Schedule";
import Guides from "./components/Guides/Guides";
import Profile from "./components/Profile/Profile";
import Layout from "./components/Layout/Layout";

import "./App.scss";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<MainPage />} />
          <Route path="schedule" element={<Schedule />} />
          <Route path="guides" element={<Guides />} />
          <Route path="profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>

  );
}

export default App;
