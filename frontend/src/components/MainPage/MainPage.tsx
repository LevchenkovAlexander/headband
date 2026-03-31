import { useNavigate } from "react-router-dom";

import "./MainPage.scss";
import guidesIcon from "../../assets/main/guids.svg";
import scheduleIcon from "../../assets/main/schedule.svg";
import profileIcon from "../../assets/main/profile.svg";

function MainPage() {
  const navigate = useNavigate();
  return (
    <div className="app-wrapper">
      <div className="mobile-version">
        <div className="header">
          <div className="header__greeting">good morning</div>
          <div className="header__version">version for masters</div>
        </div>

        <div className="actual">
          <div className="actual__header">
            <div className="actual__title">Актуальное</div>
            <span className="actual__underline"></span>
          </div>
          <div className="actual__wrapper">
            <div className="actual__event">
              <div className="actual__bar"></div>
              <div className="actual__info">
                <div className="actual__service">13:00 Покраска</div>
                <div className="actual__subservice">14:30 Мелирование</div>
              </div>
            </div>
            <div className="actual__rest">
              <div className="actual__bar actual__bar--transparent"></div>
              <div className="actual__break">Отдых 2 часа 20 минут</div>
            </div>

            <div className="actual__event">
              <div className="actual__bar"></div>
              <div className="actual__info">
                <div className="actual__service">13:00 Покраска</div>
                <div className="actual__subservice">14:30 Мелирование</div>
              </div>
            </div>
            <div className="actual__rest">
              <div className="actual__bar actual__bar--transparent"></div>
              <div className="actual__break">Отдых 2 часа 20 минут</div>
            </div>
          </div>
        </div>

        <div className="information">
          <div className="information__header">
            <div className="information__title">Информация</div>
            <div className="information__underline"></div>
          </div>
          <div className="information__wrapper">
            <div className="information__guides" onClick={() => navigate('/guides')}>            
              Гайды
              <img src={guidesIcon} className="information__svg" />
            </div>
            <div className="information__schedule" onClick={() => navigate('/schedule')}>
              Расписание
              <img src={scheduleIcon} className="information__svg information__svg--right" />
            </div>
            <div className="information__profile" onClick={() => navigate('/profile')}>
              Профиль
              <img src={profileIcon} className="information__svg information__svg" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
