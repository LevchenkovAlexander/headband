import "./register.scss";

import { Link } from "react-router-dom";

const Register = () => {
  const handleSumbit = (e: React.SyntheticEvent) => {
    e.preventDefault();
  };

  return (
    <div className="register">
      <div className="register__title">Регистрация аккаунта</div>
      <div className="register__greeting">
        Добро пожаловать в экосистему headband
      </div>
      <form className="register__form" onSubmit={handleSumbit}>
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

        <label htmlFor="repeat-password"></label>
        <input
          id="repeat-password"
          type="password"
          name="repeat-password"
          placeholder="Повторите пароль"
          required
          autoComplete="new-password"
        />

        <button className="register__submit" type="submit">
          Зарегистрироваться
        </button>
      </form>

      <div className="register__bottom">
        Уже есть аккаунт? <Link to="/authorization">Войти</Link>
      </div>
    </div>
  );
};

export default Register;
