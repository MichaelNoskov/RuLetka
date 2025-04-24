import './styles.css';
import { genders, countries, interests, appRoutes, URLs } from '../../const';
import mouse from '../../static/mouse.jpg'

import { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

import { createTheme, ThemeProvider, styled } from '@mui/material/styles';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Button from '@mui/material/Button';
import Skeleton from '@mui/material/Skeleton';

import VideoCameraFrontIcon from '@mui/icons-material/VideoCameraFront';
import LogoutIcon from '@mui/icons-material/Logout';
import SaveIcon from '@mui/icons-material/Save';


const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
        secondary: {
            main: '#EF8666'
        }
    },
});

const Item = styled(Card)(({ theme }) => ({
    position: 'relative',
    padding: theme.spacing(1),
    textAlign: 'start',
    height: 40,
    color: 'white',
    userSelect: 'none',

    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundImage: `url(${mouse})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        filter: 'brightness(0.6)',
        zIndex: 0,
        borderRadius: theme.shape.borderRadius,
      },
    
      '& > *': {
        position: 'relative',
        zIndex: 1,
      },
}));

const InterestsHitbox = styled('div')({
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    cursor: 'pointer',
    zIndex: 2,
  });

export default function ProfilePage() {
    const navigate = useNavigate()

    const [selectedInterests, setSelectedInterests] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const toggleInterest = (value) => {
        setSelectedInterests((prev) =>
            prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
        );
    };

    const [form, setForm] = useState({
        username: '',
        is_male: '',
        birthdate: '',
        country: '',
        description: '',
    });

    const [formInitial, setFormInitial] = useState({
        username: '',
        is_male: '',
        birthdate: '',
        country: '',
        description: '',
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm(prevForm => ({ ...prevForm, [name]: value }));
    };

    async function handleLogout() {
        const formData = new FormData();
        formData.append('username', form.username);
        formData.append('is_male', form.is_male);
        formData.append('birthdate', form.birthdate);
        formData.append('country', form.country);
        formData.append('description', form.description);

        console.log('clear user')

        try {
            const response = await fetch(`${URLs.backendHost}/api/logout`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при удалении');
            } 
            navigate(appRoutes.login)

        } catch (err) {
            console.log(err);
        }
    }

    async function saveChanges() {
        const formData = new FormData();
        formData.append('username', form.username);
        formData.append('is_male', form.is_male);
        formData.append('birthdate', form.birthdate);
        formData.append('country', form.country);
        formData.append('description', form.description);

        console.log('save changes attempt:', {formData})

        try {
            const response = await fetch(`${URLs.backendHost}/api/user`, {
                method: 'POST',
                body: formData,
                credentials: 'include',
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при изменении');
            }
            setFormInitial({ ...form });

        } catch (err) {
            console.log(err);
        }
    }

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await fetch(`${URLs.backendHost}/api/user/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                const userData = {
                    username: data.username || '',
                    is_male: data.is_male !== null ? data.is_male : true,
                    birthdate: data.birthdate || '',
                    country: data.country || '',
                    description: data.description || '',
                };
                setForm(userData)
                setFormInitial(userData)
                setIsLoading(false)

                // Assuming interests are returned in the userData
                // You might need to adjust this part based on your API response
                //setSelectedInterests(userData.interests || []);

            } catch (error) {
                console.error("Could not fetch user data:", error);
            }
        };

        fetchUserData();
    }, []);

    const hasChanges = () => {
        return (
          form.username !== formInitial.username ||
          form.is_male !== formInitial.is_male ||
          form.birthdate !== formInitial.birthdate ||
          form.country !== formInitial.country ||
          form.description !== formInitial.description
        );
    };

    return (
        <ThemeProvider theme={theme}>
            <Container className="profile-container">
                <Box className="header-container">
                    <p className="profile-title">Профиль</p>
                    <Box>
                        <NavLink to={appRoutes.main}>
                            <Button
                                variant="contained"
                                endIcon={<VideoCameraFrontIcon/>}
                                size='large'
                                sx={{
                                    color: 'white',
                                    fontWeight: 'bold',
                                    padding: '10px',
                                    marginRight: '10px',
                                    gap: '10px'
                                }}
                            >Запустить рулетку</Button>
                        </NavLink>
                        <NavLink to={appRoutes.login}>
                            <Button
                                variant="contained"
                                endIcon={<LogoutIcon/>}
                                size='large'
                                color='secondary'
                                sx={{
                                    color: 'white',
                                    fontWeight: 'bold',
                                    padding: '10px',
                                    gap: '10px',
                                }}
                                onClick={handleLogout}
                            >Выйти</Button>
                        </NavLink>
                    </Box>
                </Box>
                
                <hr color='#E0E0E0'/>

                <Grid container spacing={2}>
                    <Grid size={4}>
                        <Box className="personal-container">
                            <p className="interests-title">Сведения</p>

                            {isLoading ? (  // Show skeletons if loading
                                <>
                                    <Skeleton variant="rectangular" width={290} height={40} />
                                    <Skeleton variant="rectangular" width={290} height={40} />
                                    <Skeleton variant="rectangular" width={290} height={40} />
                                    <Skeleton variant="rectangular" width={290} height={40} />
                                    <p className="interests-title">Расскажите о себе</p>
                                    <Skeleton variant="rectangular" width={290} height={175} />
                                </>
                            ) : (
                                <>
                                <TextField
                                    name="username"
                                    onChange={handleChange}
                                    value={form.username}
                                    className="text-field"
                                    label="Имя"
                                    size="small"
                                />
                                <TextField
                                    name="is_male"
                                    onChange={handleChange}
                                    value={form.is_male}
                                    className="text-field"
                                    label="Пол"
                                    size="small"
                                    select>
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
                                />
                                <TextField
                                    name="country"
                                    onChange={handleChange}
                                    value={form.country}
                                    className="text-field"
                                    id="country"
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
                                <p className="interests-title">Расскажите о себе</p>
                                <TextField
                                    name="description"
                                    onChange={handleChange}
                                    value={form.description}
                                    variant='filled'
                                    multiline
                                    minRows={6}
                                    maxRows={9}
                                    inputProps={{
                                        maxLength: 500
                                    }}
                                />
                                </>
                            )}                            
                        </Box>
                    </Grid>

                    <Grid size={8}>
                        <Box className="interests-container">
                            <p className="interests-title">Ваши интересы</p>
                            <div className="interests-wrapper">
                                {interests.map((option) => {
                                return (
                                    <Item key={option.value} style={{ cursor: 'pointer' }}>
                                    <FormControlLabel
                                        control={
                                        <Checkbox
                                            checked={selectedInterests.includes(option.value)}
                                            value={option.value}
                                            onChange={() => toggleInterest(option.value)}
                                            tabIndex={0}
                                            sx={{
                                                color: 'white',
                                                '&.Mui-checked': { color: 'white'},
                                                position: 'relative',
                                                zIndex: 3,
                                            }}
                                        />
                                        }
                                        label={option.label}
                                        sx={{
                                            color: 'white',
                                            userSelect: 'none',
                                            '& .MuiFormControlLabel-label': { lineHeight: 1 },
                                        }}
                                    />
                                    <InterestsHitbox
                                        onClick={() => toggleInterest(option.value)}
                                        role="button"
                                        aria-pressed={selectedInterests.includes(option.value)}
                                        tabIndex={-1}
                                        onKeyDown={(e) => {
                                            if (e.key === ' ' || e.key === 'Enter') {
                                                e.preventDefault();
                                                toggleInterest(option.value);
                                            }
                                        }}
                                    />
                                    </Item>
                                );
                                })}
                            </div>
                            <Button
                                variant="contained"
                                startIcon={<SaveIcon/>}
                                sx={{
                                    color: 'white',
                                    fontWeight: 'bold',
                                    padding: '10px'
                                 }}
                                disabled={!hasChanges()}
                                onClick={saveChanges}
                            >Сохранить изменения</Button>
                        </Box>
                    </Grid>
                </Grid>
            </Container>
        </ThemeProvider>
    )
}