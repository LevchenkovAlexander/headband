import { useSelector } from "react-redux";
import type { RootState } from "../../storage/store";
import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

const ProtectedRoute = ({ children }: Props) => {
  const isAuth = useSelector((state: RootState) => state.auth.isAuth);

  if (!isAuth) {
    return <Navigate to="/authorization" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;