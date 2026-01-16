import MainPage from './pages/main-page/MainPage.jsx';
import RegisterPage from './pages/register-page/RegisterPage.jsx';
import LoginPage from './pages/login-page/LoginPage.jsx';
import ProfilePage from './pages/profile-page/ProfilePage.jsx';
import NotFoundPage from './pages/not-found-page/NotFoundPage.jsx';
import CheckAuth from './components/check-auth/CheckAuth.jsx';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { appRoutes } from './const.js';
import axios from 'axios';

axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';

function App() {
  return (
    <div>
      <BrowserRouter>
        <Routes>
          <Route index element={<CheckAuth><MainPage/></CheckAuth>}/>
          <Route path={appRoutes.profile} element={<CheckAuth><ProfilePage/></CheckAuth>} />
          <Route path={appRoutes.login} element={<LoginPage />} />
          <Route path={appRoutes.register} element={<RegisterPage />} />
          <Route path="*" element={<NotFoundPage />}/>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
