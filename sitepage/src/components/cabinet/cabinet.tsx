import "./cabinet.scss";
import goHome from "../../assets/icons/goHome.svg";
import quit from "../../assets/icons/quit.svg";
import Avatar from "../../assets/images/avatar.svg";
import arrowDown from "../../assets/icons/keyboard_arrow_down.svg";
import deleteIcon from "../../assets/icons/delete.svg";
import changeIcon from "../../assets/icons/change.svg";

import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setAuth } from "../../storage/authSlice";

type MasterProps = {
  id: number;
  name: string;
  tg: string;
};

type OrganizationProps = {
  id: number;
  name: string;
  address: string;
};

const SetMaster = ({ id, name, tg }: MasterProps) => {
  return (
    <div className="masters-list__item clear-glass" data-id={id}>
      <div className="masters-list__id">{id}</div>
      <div className="masters-list__name">{name}</div>
      <div className="masters-list__tg">{tg}</div>
      <div className="masters-list__expand-btn">
        <button type="button" className="expand-btn">
          <img src={arrowDown} />
        </button>
      </div>
    </div>
  );
};

const SetOrganization = ({ id, name, address }: OrganizationProps) => {
  return (
    <div className="organizations-list__item clear-glass" data-id={id}>
      <div className=""></div>
      <div className="organizations-list__id">{id}</div>
      <div className="organizations-list__name">{name}</div>
      <div className="organizations-list__address">{address}</div>

      <div className="organizations-list__actions">
        <button type="button" className="organizations-list__change-btn">
          <img src={changeIcon} />
        </button>
        <button type="button" className="organizations-list__delete-btn">
          <img src={deleteIcon} />
        </button>
      </div>
      <div className=""></div>
    </div>
  );
};

const Cabinet = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  return (
    <div className="cabinet">
      <div className="cabinet-header">
        <div className="cabinet-header__title">manage your business</div>
        <Link className="cabinet-header__back-btn clear-glass" to="/">
          <img src={goHome} alt="home" />
        </Link>
      </div>

      <div className="cabinet__field">
        <section className="cabinet-profile">
          <div className="cabinet-profile__title header-title ">Профиль</div>

          <div className="cabinet-profile__field">
            <div className="profile-user">
              <div className="profile-user__avatar">
                <img src={Avatar} alt="avatar" />
              </div>
              <button
                className="profile-user__exit-btn"
                onClick={() => {
                  navigate("/");
                  dispatch(setAuth(false));
                  localStorage.setItem("isAuth", "false");
                }}
              >
                <img src={quit} alt="quit" />
                Выйти
              </button>
            </div>

            <div className="profile-user__info">
              <div className="profile-user__email">
                <div className="row">email:</div>
                <div className="row2">pypazalypa@mail.ru</div>
              </div>

              <div className="profile-user__subscribe">
                <div className="row">подписка:</div>
                <div className="row2">до 22.08.1488</div>
              </div>

              <div className="profile-user__orgs">
                <div className="row">организаций:</div>
                <div className="row2">3</div>
              </div>

              <div className="profile-user__masters">
                <div className="row">мастеров:</div>
                <div className="row2">26</div>
              </div>

              <div className="profile-user__users">
                <div className="row">пользователей:</div>
                <div className="row2">212</div>
              </div>
            </div>
          </div>
        </section>

        <section className="cabinet-masters">
          <div className="cabinet-masters__header header-title">
            Ваши мастера
          </div>
          <div className="masters-list">
            <div className="masters-list__header">
              <div className="masters-list__header-id">id</div>
              <div className="masters-list__header-name">Имя</div>
              <div className="masters-list__header-tg">tg</div>
              <div className="masters-list__header-empty"></div>
            </div>
            <div className="masters-list__wrapper">
              <div className="masters-list__items">
                <SetMaster id={1} name="Николаев Алексей" tg="@nikaalex" />
                <SetMaster id={2} name="Ерохин Александр" tg="@erokha" />
                <SetMaster id={3} name="Ким Павел" tg="@pkim" />
                <SetMaster id={4} name="Хайруллин Олег" tg="@ekhairulla" />
                <SetMaster id={5} name="Глушенков Максим" tg="@glushonmax" />
                <SetMaster id={6} name="Левченков Александр" tg="@aaaalllle" />
                <SetMaster id={7} name="Короткий Андрей" tg="@shorty" />
              </div>
            </div>
          </div>
        </section>

        <section className="cabinet-organizations">
          <div className="cabinet-organizations__header">
            <div className="cabinet-organizations__header-title">
              Ваши организации
            </div>
            <button
              type="button"
              className="cabinet-organizations__header-add-btn clear-glass"
            >
              Добавить акции
            </button>
          </div>

          <div className="organizations-list">
            <div className="organizations-list__header">
              <div className="organizations-list__header-id">id</div>
              <div className="organizations-list__header-name">
                Название организации
              </div>
              <div className="organizations-list__header-address">Адрес</div>
              <div className="organizations-list__header-empty"></div>
            </div>
            <div className="organizations-list__wrapper">
              <div className="organizations-list__items">
                <SetOrganization
                  id={1}
                  name="“Обретая крылья”"
                  address="Шуваловский пр-кт, 31"
                />
                <SetOrganization
                  id={2}
                  name="Салон С. Акатьевой"
                  address="Невский пр-кт, 12"
                />
                <button
                  type="button"
                  className="organizations-list__add-btn clear-glass"
                >
                  Добавить организацию...
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Cabinet;
