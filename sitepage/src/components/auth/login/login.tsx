import "./login.scss";

import { Link } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { setAuth } from "../../../storage/authSlice";

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSumbit = (e: React.SyntheticEvent) => {
    e.preventDefault();
    dispatch(setAuth(true));
    localStorage.setItem("isAuth", "true");
    navigate("/cabinet", { replace: true });
  };

  return (
    <div className="login">
      <div className="login__title">Войти в аккаунт</div>
      <div className="login__greeting">
        Добро пожаловать в экосистему headband
      </div>
      <form className="login__form" onSubmit={handleSumbit}>
        <label htmlFor="email"></label>
        <input
          id="email"
          type="email"
          name="email"
          placeholder="Почта"
          required
          autoComplete="username"
        />

        <label htmlFor="password"></label>
        <input
          id="password"
          type="password"
          name="password"
          placeholder="Пароль"
          required
          autoComplete="current-password"
        />

        <div className="login__controls">
          <a href="#" className="login__forgot">
            Забыли пароль?
          </a>

          <label className="login__remember">
            <input type="checkbox" name="remember" />
            <span>Запомнить меня</span>
          </label>
        </div>

        <button className="login__submit" type="submit">
          Войти
        </button>
      </form>
      <button className="login__yandex penis" type="button">
        Войти с Яндекс ID
      </button>

      <div className="login__bottom">
        Нет аккаунта? <Link to="/registration">Создать</Link>
      </div>
    </div>
  );
};

export default Login;
