import './page404.scss';

import { Link } from 'react-router-dom';

const Page404 = () => {
    return (
        <div className="wrapper">
            <div style={{'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '24px'}}>Страница не найдена</div>
            <Link type="button"  style={{'display': 'block', 'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '24px', 'marginTop': '30px'}} to='/'>Вернуться назад</Link>
        </div>
        
    );
}

export default Page404;