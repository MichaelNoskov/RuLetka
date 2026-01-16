import Cookies from 'js-cookie';
import { useNavigate } from "react-router";
import { appRoutes } from "../../const";
import { useEffect, useState } from "react";

const CheckAuth = ({ children }) => {
    const navigate = useNavigate();
    const [isChecking, setIsChecking] = useState(true);
    const [isAuthorized, setIsAuthorized] = useState(false);
    
    // Имя куки из settings.COOKIE_NAME (замени на реальное!)
    const COOKIE_NAME = 'access_token'; 

    useEffect(() => {
        const checkAuth = async () => {
            const token = Cookies.get(COOKIE_NAME);
            
            if (!token) {
                console.log('unauthorized: no token');
                setIsChecking(false);
                navigate(appRoutes.login, { replace: true });
                return;
            }

            // Проверяем токен через защищенный API
            try {
                const response = await fetch('/api/user/', {
                    method: 'GET',
                    credentials: 'include', // Отправляем httponly куки
                });

                if (response.ok) {
                    console.log('✅ authorized: token valid');
                    setIsAuthorized(true);
                } else {
                    console.log('❌ unauthorized: token invalid');
                    Cookies.remove(COOKIE_NAME);
                }
            } catch (error) {
                console.log('❌ unauthorized: check failed');
                Cookies.remove(COOKIE_NAME);
            }
            
            setIsChecking(false);
        };

        checkAuth();
    }, [navigate]);

    // Пока проверяем - показываем loader
    if (isChecking) {
        return <div>Проверка авторизации...</div>;
    }

    // Токен валиден - рендерим children
    if (isAuthorized) {
        return children;
    }

    // Не авторизован - редирект уже сработал
    return null;
};

export default CheckAuth;
