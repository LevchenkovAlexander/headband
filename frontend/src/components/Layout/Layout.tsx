import "./Layout.scss";

import { Outlet } from "react-router-dom";

function Layout() {
  return (
    <div className="app-wrapper">
      <div className="mobile-version">
        <Outlet />
      </div>
    </div>
  );
}

export default Layout;
