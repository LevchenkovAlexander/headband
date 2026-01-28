import "./App.scss";
import scissors from "../../assets/images/scissors.png";
import ai from "../../assets/icons/AI.svg";
import individ from "../../assets/icons/individ.svg";
import master from "../../assets/icons/master.svg";
import nice from "../../assets/icons/nice.svg";
import recording from "../../assets/icons/recording.svg";
import telegram from "../../assets/icons/telegram.svg";
import galka from "../../assets/icons/galka.svg";

type TitleProps = {
  text: string;
};

type CardsWhyProps = {
  icon: string;
  title: string;
  text: string;
};

const App = () => {
  const Title = ({ text }: TitleProps) => {
    return (
      <div className="title">
        <span>{text}</span>
      </div>
    );
  };

  const CardWhy = ({ icon, title, text }: CardsWhyProps) => {
    return (
      <div className="why-card">
        <img className="why-card__icon" src={icon} />
        <div className="why-card__title">{title}</div>
        <div className="why-card__text">{text}</div>
      </div>
    );
  };

  const SpisokText = ({ text }: TitleProps) => {
    return (
      <div className="price-list__item">
        <img src={galka} />
        <div className="price-list__item-text">{text}</div>
      </div>
    );
  };

  return (
    <div className="main">
      <div className="header">
        <div className="header__title">headband</div>
        <button type="button" className="header__support">
          Поддержка
        </button>
      </div>

      <div className="start">
        <div className="start__left">
          <Title text="Let’s start!" />
          <div className="promo">
            <div className="promo__title">
              Удобный и стильный сайт для Вашего салона красоты
            </div>
            <div className="promo__text">
              Профессиональные сайты с онлайн-записью, гайдами для мастеров, ai
              предпросмотром для клиентов, а также с удобным тг ботом для
              пользователей любой категории.
            </div>
            <div className="promo__actions">
              <button
                type="button"
                className="promo__btn promo__btn--subscribe"
              >
                Перейти к подписке
              </button>
              <button type="button" className="promo__btn promo__btn--example">
                Пример сайта
              </button>
            </div>
          </div>
        </div>

        <div className="start__right">
          <img src={scissors} alt="scissors" />
        </div>
      </div>

      <div className="why">
        <Title text="Why we?" />
        <div className="why__wrapper">
          <div className="why__field">
            <CardWhy
              icon={nice}
              title="Красивый сайт"
              text="Приятный, понятный и современный дизайн, который оценят и мастера, и клиенты "
            />
            <CardWhy
              icon={recording}
              title="Онлайн - запись"
              text="Позвольте клиентам записываться за пару кликов в любое удобное для них время"
            />
            <CardWhy
              icon={telegram}
              title="Телеграм бот"
              text="Поможет напомнить клиенту о предстоящей записи, а мастеру выведет расписание"
            />
            <CardWhy
              icon={ai}
              title="AI предпросмотр"
              text="Поможет клиенту определиться с желаемым стилем перед записью. Мастер же получит информацию о предстоящей задаче"
            />
            <CardWhy
              icon={master}
              title="Гайды для мастера"
              text="Материалы для мастеров с подсказками по разным стилям, собранные другими мастерами и дополненные ИИ"
            />
            <CardWhy
              icon={individ}
              title="Индвидуальность"
              text="Настройте сайт под свой бизнес в нашем гибком конструкторе"
            />
          </div>
        </div>
      </div>

      <div className="price">
        <Title text="Our Price" />
        <div className="price__wrapper">
          <div className="price__field">
            <div className="price__header">
              <div className="price__title">Начни с headband</div>
              <div className="price__price">
                <span className="price__value">3000₽</span>
                <span className="price__period">/мес</span>
              </div>
            </div>
            <div className="price-list">
              <SpisokText text="отдельные mini App и боты для мастера и клиента" />
              <SpisokText text="ежедневная поддержка от разработчиков" />
              <SpisokText text="возможность настройки и добавления услуг" />
              <SpisokText text="выставления собственного прайс листа" />
              <SpisokText text="настройка для мастеров, а также привязка к телеграм" />
              <SpisokText text="удобная визуализация расписания для мастеров" />
              <SpisokText text="бесплатный ИИ инструмент для примерки прически" />
              <SpisokText text="возможность связи с 2GIS и др. для отображения отзывов" />
            </div>
            <button type="button" className="price__btn">
              Оформить
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
