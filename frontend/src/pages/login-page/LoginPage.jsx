import './styles.css';
import { appRoutes, URLs } from '../../const';

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';



const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
    },
});

export default function LoginPage() {
    // const dispatch = useDispatch()
    const navigate = useNavigate()

    const [username, setUsername] = useState('');
    const handleUsernameChange = (event) => setUsername(event.target.value);
    const [password, setPassword] = useState('');
    const handlePasswordChange = (event) => setPassword(event.target.value);
    const [error, setError] = useState();

    function validateForm() {
        if (!username || !password) {
            setError('Пожалуйста, заполните все поля');
            return false;
        }
        // if (username.length < 4) {
        //     setError('Логин должен содержать минимум 4 символа');
        //     return false;
        // }
        // if (password.length < 4) {
        //     setError('Пароль должен содержать минимум 4 символа');
        //     return false;
        // }
        setError(null);
        return true;
    }

    async function handleLogin() {
        if (!validateForm()) {
            return;
        }

        console.log('login attempt')

        try {
            // Формируем данные для отправки в формате application/x-www-form-urlencoded,
            // так как backend ожидает OAuth2PasswordRequestForm
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${URLs.backendHost}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
                credentials: 'include', // чтобы куки с токеном сохранились
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при входе');
            }

            // Успешный вход
            // Можно обновить состояние пользователя в redux или context
            // dispatch(
            //     setUser(
            //         {
            //             user: response.data,
            //             token: response.data.accessToken
            //         }
            //     )
            // )
            navigate('/'); // Перенаправление после успешного входа
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <ThemeProvider theme={theme}>
            <Stack
                direction="row"
                justifyContent="center"
                alignItems="center"
                sx={{ height: "100vh" }}
            >
                <Box className="login-container">
                    <p className="title">Вход в систему</p>
                    <TextField
                        onChange={handleUsernameChange}
                        value={username}
                        className="text-field"
                        label="Логин"
                        size="small"
                        error={error}
                    />
                    <TextField
                        onChange={handlePasswordChange}
                        value={password}
                        className="text-field"
                        label="Пароль"
                        size="small"
                        type="password"
                        error={error}
                    />

                    {error && <p style={{ color: 'red', margin: 0}}>{error}</p>}

                    <Button
                        className="login-button"
                        variant="contained"
                        color="primary"
                        sx={{
                            color: 'white',
                            fontWeight: 'bold',
                            padding: '10px',
                        }}
                        disabled={(!username || !password)}
                        onClick={handleLogin}
                    >Войти</Button>
                    <a className="subtitle" href={appRoutes.register}>Нет аккаунта? Зарегистрироваться</a>
                </Box>
            </Stack>
        </ThemeProvider>
    )
}