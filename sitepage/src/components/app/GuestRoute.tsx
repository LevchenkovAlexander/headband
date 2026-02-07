import { useSelector } from "react-redux";
import type { RootState } from "../../storage/store";
import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

const GuestRoute = ({ children }: Props) => {
  const isAuth = useSelector((state: RootState) => state.auth.isAuth);

  if (isAuth) {
    return <Navigate to="/profile" replace />;
  }

  return <>{children}</>;
};

export default GuestRoute;