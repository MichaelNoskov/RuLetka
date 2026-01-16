import './styles.css';
import { genders, countries, interests, appRoutes, URLs } from '../../const';
import { useAvatar } from '../../hooks/useAvatar';
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
import Alert from '@mui/material/Alert';
import Avatar from '@mui/material/Avatar';

import VideoCameraFrontIcon from '@mui/icons-material/VideoCameraFront';
import LogoutIcon from '@mui/icons-material/Logout';
import SaveIcon from '@mui/icons-material/Save';
import CheckIcon from '@mui/icons-material/Check';


const theme = createTheme({
    palette: {
        primary: { main: '#7394EE' },
        secondary: { main: '#EF8666' }
    },
});

const getBackgroundImage = (value) => {
    const url = `/static/img-${value}.jpg`;
    return url;
};

const Item = styled(Card)(({ theme, bgimage }) => ({
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
        backgroundImage: `url(${bgimage}), url(${mouse})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        filter: 'brightness(0.5)',
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
    zIndex: 3,
});

export default function ProfilePage() {
    const navigate = useNavigate()
    const [selectedInterests, setSelectedInterests] = useState([]);
    const [selectedInterestsInitial, setSelectedInterestsInitial] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [saveLoading, setSaveLoading] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [saveError, setSaveError] = useState('');

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

    const { avatarUrl, avatarLoading, handleAvatarClick } = useAvatar();

    const toggleInterest = (value) => {
        setSelectedInterests((prev) =>
            prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
        );
    };

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm(prevForm => ({ ...prevForm, [name]: value }));
    };

    async function handleLogout() {
        console.log('clear user')

        try {
            const response = await fetch(`${URLs.backendHost}/auth/logout`, {
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
        setSaveLoading(true);
        setSaveSuccess(false);
        setSaveError('');

        const formData = new FormData();
        formData.append('username', form.username);
        formData.append('is_male', form.is_male);
        formData.append('birthdate', form.birthdate);
        formData.append('country', form.country);
        formData.append('description', form.description);
        // formData.append('interests', JSON.stringify(selectedInterests));

        try {
            const response = await fetch(`${URLs.backendHost}/api/profile/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: form.username,
                    is_male: form.is_male,
                    birthdate: form.birthdate,
                    country: form.country,
                    description: form.description
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка при изменении');
            }

            setFormInitial({ ...form });
            setSelectedInterestsInitial(selectedInterests);
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 2000);
        } catch (err) {
            console.log(err);
            setSaveError(err.message || 'Не удалось сохранить изменения');
        } finally {
            setSaveLoading(false);
        }
    }

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userResponse = await fetch(`${URLs.backendHost}/api/user/`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                });
    
                if (userResponse.ok) {
                    const data = await userResponse.json();
                    const userData = {
                        username: data.username || '',
                        is_male: data.is_male !== null ? data.is_male : true,
                        birthdate: data.birthdate || '',
                        country: data.country || '',
                        description: data.description || '',
                    };
                    setForm(userData);
                    setFormInitial(userData);
                }
                setIsLoading(false);
    
            } catch (error) {
                console.error("Ошибка загрузки данных:", error);
                setIsLoading(false);
            }
        };
    
        fetchUserData();
    }, []);  

    function arraysEqual(a, b) {
        if (a === b) return true;
        if (a == null || b == null) return false;
        if (a.length !== b.length) return false;
      
        const aSorted = [...a].sort();
        const bSorted = [...b].sort();
      
        for (let i = 0; i < aSorted.length; ++i) {
          if (aSorted[i] !== bSorted[i]) return false;
        }
        return true;
    }

    const hasChanges = () => {
        return (
          form.username !== formInitial.username ||
          form.is_male !== formInitial.is_male ||
          form.birthdate !== formInitial.birthdate ||
          form.country !== formInitial.country ||
          form.description !== formInitial.description ||
          !arraysEqual(selectedInterests, selectedInterestsInitial)
        );
    };    

    return (
        <ThemeProvider theme={theme}>
            <Container className="profile-container">
                <Box className="header-container">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {avatarLoading ? (
                            <Skeleton variant="circular" width={50} height={50} />
                        ) : (
                            <Avatar 
                                src={avatarUrl || undefined} 
                                alt={form.username}
                                onClick={handleAvatarClick}
                                sx={{ 
                                    width: 50, 
                                    height: 50,
                                    bgcolor: 'primary.main',
                                    cursor: 'pointer',
                                    '&:hover': {
                                        filter: 'brightness(0.7)',
                                        transition: 'all 0.2s ease'
                                    }
                                }}
                            >
                            {form.username ? form.username.charAt(0).toUpperCase() : '?'}
                        </Avatar>
                        )}

                        {isLoading ? (
                            <Skeleton variant="text" width={240} height={50} />
                        ) : (
                            <TextField
                            name="username"
                            onChange={handleChange}
                            value={form.username}
                            variant="standard"
                            sx={{
                                '& .MuiInput-underline:before': {
                                    borderBottomColor: 'rgba(255,255,255,0.5)'
                                },
                                '& .MuiInputBase-input': {
                                    fontSize: '24px',
                                    fontWeight: 'bold',
                                }
                            }}
                            />
                        )}
                    </Box>
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
                                    <p className="interests-title">Расскажите о себе</p>
                                    <Skeleton variant="rectangular" width={290} height={175} />
                                </>
                            ) : (
                                <>
                                <TextField
                                    name="is_male"
                                    onChange={handleChange}
                                    value={form.is_male}
                                    className="text-field"
                                    label="Пол"
                                    size="small"
                                    select>
                                    {genders.slice(1).map((option) => (
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
                                    {countries.slice(1).map((option) => (
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
                                {interests && interests.length > 0 ? (
                                    <div className="interests-wrapper">
                                        {interests.map((option) => {
                                            const bgImage = getBackgroundImage(option.value)
                                            return (
                                                <Item key={option.value} bgimage={bgImage} style={{ cursor: 'pointer' }}>
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
                                ) : (
                                    <Container className='message-container'>
                                        <p className="interests-title">Похоже, интересы еще не загружены в систему</p>
                                    </Container>
                                )}
                            <Button
                                variant="contained"
                                sx={{
                                    color: 'white',
                                    fontWeight: 'bold',
                                    padding: '10px'
                                }}
                                disabled={!hasChanges() || saveLoading}
                                loading={saveLoading}
                                startIcon={saveSuccess ? <CheckIcon /> : <SaveIcon />}
                                onClick={saveChanges}
                            >
                                {saveSuccess ? 'Сохранено!' : 'Сохранить изменения'}
                            </Button>

                            {saveError && (
                            <Alert severity="error" sx={{ marginTop: '0px' }}>
                                {saveError}
                            </Alert>
                            )}
                        </Box>
                    </Grid>
                </Grid>
            </Container>
        </ThemeProvider>
    )
}