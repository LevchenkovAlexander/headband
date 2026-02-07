import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "../homepage/homepage";
import Page404 from "../page404/page404";
import AuthTemplate from "../auth/auth";
import Login from "../auth/login/login";
import Register from "../auth/register/register";
import Organization from "../form-to-create/organization/organization";
import Profile from "../profile/profile";
import ProtectedRoute from "./ProtectedRoute";
import GuestRoute from "./GuestRoute";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/authorization"
          element={
            <GuestRoute>
              <AuthTemplate title="authorization">
                <Login />
              </AuthTemplate>
            </GuestRoute>
          }
        />
        <Route
          path="/registration"
          element={
            <GuestRoute>
              <AuthTemplate title="registration">
                <Register />
              </AuthTemplate>
            </GuestRoute>
          }
        />
        <Route path="/form-to-create-org" element={<Organization />} />
        <Route path="*" element={<Page404 />} />
      </Routes>
    </Router>
  );
};

export default App;
