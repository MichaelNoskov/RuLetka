import './styles.css';
import { appRoutes, genders, countries, URLs } from '../../const';

import { useState } from 'react';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import { useNavigate } from 'react-router-dom';


const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
    },
});

export default function RegisterPage() {
    const navigate = useNavigate()

    const [form, setForm] = useState({
        username: '',
        password: '',
        passwordConfirm: '',
        is_male: '',
        birthdate: '',
        country: ''
    });

    const [errors, setErrors] = useState({
        general: '',
        username: '',
        password: '',
        birthdate: ''
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm(prevForm => ({ ...prevForm, [name]: value }));
    };

    function checkError(condition, field, message) {
        if (condition) {
            setErrors(prev => ({ ...prev, [field]: message }));
            return false;
        } else {
            setErrors(prev => ({ ...prev, [field]: '' }));
            return true;
        }
    }

    const validateForm = () => {
        let isValid = true;

        isValid = checkError(
            !Object.values(form).every(val => val !== ''),
            'general',
            'Пожалуйста, заполните все поля'
        ) && isValid;

        isValid = checkError(
            form.username.length > 50,
            'username',
            'Логин не должен превышать 50 символов'
        ) && isValid;

        isValid = checkError(
            form.password.length < 8 || form.password.length > 128,
            'password',
            'Пароль должен содержать от 8 до 128 символов'
        ) && checkError(
            form.password !== form.passwordConfirm,
            'password',
            'Пароли не совпадают'
        ) && isValid;

        // isValid = checkError(
        //     form.password !== form.passwordConfirm,
        //     'password',
        //     'Пароли не совпадают'
        // ) && isValid;

        const birthDateObj = new Date(form.birthdate);
        const now = new Date();

        isValid = checkError(
            isNaN(birthDateObj.getTime()),
            'birthdate',
            'Некорректная дата рождения'
        ) && checkError(
            birthDateObj > now,
            'birthdate',
            'Дата рождения не может быть в будущем'
        ) && checkError(
            birthDateObj.getFullYear() < 1900,
            'birthdate',
            'Дата рождения слишком старая'
        ) && isValid;

        return isValid;
    };
    
    async function handleRegister() {
        if (!validateForm()) {
            return;
        }

        console.log('registration attempt')

        console.log(JSON.stringify({
            username: form.username,
            password: form.password,
            is_male: form.is_male,
            birthdate: form.birthdate,
            country: form.country,
        }))

        try {
            const response = await fetch(`${URLs.backendHost}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: form.username,
                    password: form.password,
                    is_male: form.is_male,
                    birthdate: form.birthdate,
                    country: form.country,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при регистрации');
            }

            // Успешная регистрация, можно сразу перейти на страницу логина
            navigate(appRoutes.login);
        } catch (err) {
            setErrors(prevErrors => ({ ...prevErrors, general: err}));
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
                <Box className="register-container">
                    <p className="title">Регистрация</p>
                    <TextField
                        name="username"
                        onChange={handleChange}
                        value={form.username}
                        className="text-field"
                        label="Логин"
                        size="small"
                        error={errors.username}
                        helperText={errors.username}
                    />
                    <TextField
                        name="password"
                        onChange={handleChange}
                        value={form.password}
                        className="text-field"
                        label="Пароль"
                        size="small"
                        type="password"
                        error={errors.password}
                    />
                    <TextField
                        name="passwordConfirm"
                        onChange={handleChange}
                        value={form.passwordConfirm}
                        className="text-field"
                        label="Пароль (повторно)"
                        size="small"
                        type="password"
                        error={errors.password}
                        helperText={errors.password}
                    />
                    <TextField
                        name="is_male"
                        onChange={handleChange}
                        value={form.is_male}
                        className="text-field"
                        label="Пол"
                        size="small"
                        select
                    >
                        {genders.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </TextField>
                    <TextField
                        name="birthdate"
                        onChange={handleChange}
                        value={form.birthdate}
                        className="text-field"
                        label="Дата рождения"
                        size="small"
                        type="date"
                        slotProps={{ inputLabel: {shrink: true} }}
                        error={errors.birthdate}
                        helperText={errors.birthdate}
                    />
                    <TextField
                        name="country"
                        onChange={handleChange}
                        value={form.country}
                        className="text-field"
                        label="Страна"
                        size="small"
                        select
                    >
                        {countries.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </TextField>

                    {/* {errors.general && <p style={{ color: 'red', margin: 0}}>{errors.general}</p>} */}
                    
                    <Button
                            className="register-button"
                            variant="contained"
                            color="primary"
                            sx={{
                                color: 'white',
                                fontWeight: 'bold',
                                padding: '10px',
                            }}
                            disabled={Boolean(errors.general)}
                            onClick={handleRegister}
                    >Зарегистрироваться</Button>
                    <a className="subtitle" href={appRoutes.login}>Есть аккаунт? Войти</a>
                </Box>
            </Stack>
        </ThemeProvider>
    )
}