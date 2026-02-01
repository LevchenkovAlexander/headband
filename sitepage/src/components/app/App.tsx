import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "../homepage/homepage";
import Page404 from "../page404/page404";
import AuthTemplate from "../auth/auth";
import Login from "../auth/login/login";
import Register from "../auth/register/register";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/authorization" element={<AuthTemplate title="authorization"><Login/></AuthTemplate>} />
        <Route path="/registration" element={<AuthTemplate title="registration"><Register/></AuthTemplate>} />
        <Route path="*" element={<Page404 />} />
      </Routes>
    </Router>
  );
};

export default App;
