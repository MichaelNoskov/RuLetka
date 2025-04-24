import './styles.css';
import { genders, countries, appRoutes } from '../../const';
import { initiateConnection, disconnect } from '../../services/client';

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
// import Rating from '@mui/material/Rating';

import CallIcon from '@mui/icons-material/Call';
import CallEndIcon from '@mui/icons-material/CallEnd';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import NoPhotographyIcon from '@mui/icons-material/NoPhotography';
import MicOffIcon from '@mui/icons-material/MicOff';
import PersonIcon from '@mui/icons-material/Person';



const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
        secondary: {
            main: '#565967'
        }
    },
});

const MainPage = function(){
    const navigate = useNavigate()

    const [form, setForm] = useState({
        country: '',
        is_male: '',
        age: ''
    });    
    
    const [isCalling, setIsCalling] = useState(false);
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);

    useEffect(() => {
        window.localVideo = document.getElementById('localVideo');
        window.remoteVideo = document.getElementById('remoteVideo');
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm(prevForm => ({ ...prevForm, [name]: value }));
    };

    const handleCallStart = async () => {
        console.log('call start')
        setIsCalling(true);
        try {
            await initiateConnection();
        } catch (error) {
            console.error("Failed to initiate connection:", error);
            setIsCalling(false);
        }
    };
  
    const handleCallEnd = () => {
        console.log('call end')
        setIsCalling(false);
        disconnect();
        // navigate(appRoutes.profile)
    };
  
    const handleSkipNext = () => {
        console.log('call skip')
    };

    return (
        <ThemeProvider theme={theme}>
            {/* <Box className="rating-box">
                <Box className="rating-container">
                    <p className="rating-text">
                        Оцените, насколько ваши предпочтения совпали с интересами собеседника:
                    </p>
                    <Rating name="rating" />
                </Box>
            </Box> */}

            <Box className="centered-container">
                <Box className="aspect-ratio-box">
                    <Box className="video-container-focus">
                        <div id="audioContent"></div>
                        <video id="remoteVideo" ref={remoteVideoRef} autoPlay className='video'></video>
                    </Box>
                    <Box className="video-container-mini">
                        <video id="localVideo" ref={localVideoRef} autoPlay muted className='video'></video>
                    </Box>
                </Box>
            </Box>

            <Box className="footer-box">
                <Grid container spacing={1}>
                    <Grid size={4}>
                        <Box className="search-params-box">
                            <Grid container spacing={1}>
                                <Grid size={12}>
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
                                </Grid>
                                <Grid size={8}>
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
                                </Grid>
                                <Grid size={4}>
                                    <TextField
                                        name="age"
                                        onChange={(e) => {
                                            // Allow empty string or only digits
                                            const val = e.target.value;
                                            if (val === '' || /^[0-9]+$/.test(val)) {
                                                handleChange(e);
                                            }
                                        }}
                                        value={form.age}
                                        className="text-field"
                                        label="Возраст"
                                        size="small"
                                        inputProps={{
                                            inputMode: 'numeric',
                                            pattern: '[0-9]*',
                                            maxLength: 2
                                        }}
                                    />
                                </Grid>
                            </Grid>
                        </Box>
                    </Grid>



                    <Grid size={4}>       
                        <Box className="buttons-box">
                            {!isCalling ? (
                                <IconButton
                                    id="connect"
                                    className="control-button"
                                    onClick={handleCallStart}
                                    sx={{ backgroundColor: '#6DD589', '&:hover': {backgroundColor: '#49AC81'} }}
                                >
                                    <CallIcon sx={{ color: '#FFFFFF', fontSize: 60 }} />
                                </IconButton>
                            ) : (
                                <>
                                    <IconButton
                                        id="disconnect"
                                        className="control-button"
                                        onClick={handleCallEnd}
                                        sx={{ backgroundColor: '#EF8666', '&:hover': {backgroundColor: '#C45E4E'} }}
                                    >
                                        <CallEndIcon sx={{ color: '#FFFFFF', fontSize: 60 }} />
                                    </IconButton>

                                    <IconButton
                                        className="control-button"
                                        onClick={handleSkipNext}
                                        sx={{ backgroundColor: '#7394EE', '&:hover': {backgroundColor: '#4D73C5'} }}
                                    >
                                        <SkipNextIcon sx={{ color: '#FFFFFF', fontSize: 60 }}/>
                                    </IconButton>
                                </>
                            )}
                            <IconButton
                                className="control-button"
                                sx={{ backgroundColor: '#D6D6DA', '&:hover': {backgroundColor: '#B5B5BA'} }}
                            >
                                <NoPhotographyIcon sx={{ color: '#565967', fontSize: 25 }}/>
                            </IconButton>

                            <IconButton
                                className="control-button"
                                sx={{ backgroundColor: '#D6D6DA', '&:hover': {backgroundColor: '#B5B5BA'} }}
                            >
                                <MicOffIcon sx={{ color: '#565967', fontSize: 25 }}/>
                            </IconButton>
                        </Box>
                    </Grid>

                    <Grid size={4}>
                        <Box className="profile-params-box">
                            {!isCalling ? (
                                <NavLink to={appRoutes.profile}>
                                    <Button
                                        variant="outlined"
                                        startIcon={<PersonIcon/>}
                                        color='secondary'
                                        disabled={isCalling}
                                        sx={{
                                            fontSize: '20px',
                                            fontWeight: 'bold',
                                            padding: '20px',
                                        }}
                                    >Профиль</Button>
                                </NavLink>
                            ) : (
                                <></>
                            )}
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </ThemeProvider>
    )
}

export default MainPage