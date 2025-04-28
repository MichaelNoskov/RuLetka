import './styles.css';
import { appRoutes, URLs } from '../../const';

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';


const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
    },
});

export default function LoginPage() {
    const navigate = useNavigate()
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState();

    const [form, setForm] = useState({
        username: '',
        password: '',
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm(prevForm => ({ ...prevForm, [name]: value }));
        setIsSubmitting(false);
    };

    function validateForm() {
        if (!form.username || !form.password) {
            setError('Пожалуйста, заполните все поля');
            return false;
        }
        setError(null);
        return true;
    }

    async function handleLogin() {
        if (!validateForm()) {
            setIsSubmitting(true);
            return;
        }

        setIsSubmitting(true);
        console.log('login attempt')

        try {
            const formData = new URLSearchParams();
            formData.append('username', form.username);
            formData.append('password', form.password);

            const response = await fetch(`${URLs.backendHost}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
                credentials: 'include',
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при входе');
            }

            setIsSubmitting(false);
            navigate('/');
        } catch (err) {
            setError(err.message);
            setIsSubmitting(false);
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
                        name="username"
                        onChange={handleChange}
                        value={form.username}
                        className="text-field"
                        label="Логин"
                        size="small"
                        error={error}
                    />
                    <TextField
                        name="password"
                        onChange={handleChange}
                        value={form.password}
                        className="text-field"
                        label="Пароль"
                        size="small"
                        type="password"
                        error={error}
                    />

                    {error && (
                    <Alert severity="error" sx={{ marginTop: '0px' }}>
                        {error}
                    </Alert>
                    )}

                    <Button
                        className="login-button"
                        variant="contained"
                        color="primary"
                        sx={{
                            color: 'white',
                            fontWeight: 'bold',
                            padding: '10px',
                        }}
                        disabled={isSubmitting}
                        onClick={handleLogin}
                    >Войти</Button>
                    <a className="subtitle" href={appRoutes.register}>Нет аккаунта? Зарегистрироваться</a>
                </Box>
            </Stack>
        </ThemeProvider>
    )
}