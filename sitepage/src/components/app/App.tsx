import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import HomePage from '../homepage/homepage';
import Page404 from '../page404/page404';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<HomePage/>} />
        <Route path='*' element={<Page404/>} />
      </Routes>
    </Router>
  );
};

export default App;
