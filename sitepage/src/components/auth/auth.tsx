import "./auth.scss";

import type { ReactNode } from "react";

type AuthProps = {
  title: string;
  children: ReactNode;
};

const AuthTemplate = ({ title, children }: AuthProps) => {
  return (
    <div className="auth">
      <div className="auth__title">{title}</div>
      <div className="auth__form">{children}</div>
    </div>
  );
};

export default AuthTemplate;
