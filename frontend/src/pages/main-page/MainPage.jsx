import './styles.css';
import { genders, countries, appRoutes } from '../../const';
import { initiateConnection, disconnect, toggleAudioMute, toggleVideoMute } from '../../services/client';

import React, { useState, useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Avatar from '@mui/material/Avatar';
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
    const [isCalling, setIsCalling] = useState(false);
    const [IsMuteVideo, SetIsMuteVideo] = useState(false);
    const [IsMuteAudio, SetIsMuteAudio] = useState(false);
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);

    const [searchForm, setSearchForm] = useState({
        country: '',
        is_male: '',
        age: ''
    });

    const prepareSearchParameters = (form) => {
        const formData = new FormData();
    
        if (form.country && form.country !== '') {formData.append('country', form.country);}    
        if (form.is_male !== '') {formData.append('is_male', form.is_male);}
        if (form.age !== '') {formData.append('age', parseInt(form.age, 10));}
    
        return formData;
    };

    useEffect(() => {
        window.localVideo = document.getElementById('localVideo');
        window.remoteVideo = document.getElementById('remoteVideo');
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setSearchForm(prevForm => ({ ...prevForm, [name]: value }));
    };

    const handleCallStart = async () => {
        console.log('call start')
        setIsCalling(true);
        try {
            const searchParameters = prepareSearchParameters(searchForm);
            await initiateConnection({ audio: !IsMuteAudio, video: !IsMuteVideo, searchParameters: JSON.stringify(searchParameters) });
        } catch (error) {
            console.error("Failed to initiate connection:", error);
            setIsCalling(false);
        }
    };
  
    const handleCallEnd = () => {
        console.log('call end')
        setIsCalling(false);
        disconnect();
    };
  
    const handleSkipNext = () => {
        console.log('call skip')
    };

    useEffect(() => {
        if (isCalling) {
            toggleAudioMute(IsMuteAudio);
        }
    }, [IsMuteAudio, isCalling]);

    useEffect(() => {
        if (isCalling) {
            toggleVideoMute(IsMuteVideo);
            // const localVideo = document.getElementById('localVideo');
            // if (localVideo) {
            //     localVideo.style.display = IsMuteVideo ? 'none' : 'block';
            // }
        }
    }, [IsMuteVideo, isCalling]);

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
                        <Avatar sx={{ bgcolor: '#FFF6EE', width: 350, height: 350, position: 'absolute' }}>
                            <PersonIcon sx={{ color: '#CE9595', fontSize: 250 }} />
                        </Avatar>
                        <div id="audioContent"></div>
                        <video id="remoteVideo" ref={remoteVideoRef} autoPlay className='video'></video>
                    </Box>
                    <Box className="video-container-mini">
                        <Avatar sx={{ bgcolor: '#EEF5FF', width: 100, height: 100, position: 'absolute'  }}>
                            <PersonIcon sx={{ color: '#9599CE', fontSize: 65 }} />
                        </Avatar>
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
                                        value={searchForm.country}
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
                                        value={searchForm.is_male}
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
                                        value={searchForm.age}
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
                                onClick={() => SetIsMuteVideo(!IsMuteVideo)}
                                sx={{
                                    backgroundColor: IsMuteVideo ? '#D54D4D' : '#D6D6DA',
                                    '&:hover': {
                                    backgroundColor: IsMuteVideo ? '#B41B1B' : '#B5B5BA',
                                    },
                                }}
                                >
                                <NoPhotographyIcon
                                    sx={{
                                    color: IsMuteVideo ? '#FFFFFF' : '#565967',
                                    fontSize: 25,
                                    }}
                                />
                            </IconButton>

                            <IconButton
                                className="control-button"
                                onClick={() => SetIsMuteAudio(!IsMuteAudio)}
                                sx={{
                                    backgroundColor: IsMuteAudio ? '#D54D4D' : '#D6D6DA',
                                    '&:hover': {
                                    backgroundColor: IsMuteAudio ? '#B41B1B' : '#B5B5BA',
                                    },
                                }}
                                >
                                <MicOffIcon
                                    sx={{
                                    color: IsMuteAudio ? '#FFFFFF' : '#565967',
                                    fontSize: 25,
                                    }}
                                />
                            </IconButton>
                        </Box>
                    </Grid>

                    <Grid size={4}>
                        <Box className="profile-params-box">
                            <NavLink
                                to={appRoutes.profile}
                                style={isCalling ? { pointerEvents: 'none' } : {}}
                                tabIndex={isCalling ? -1 : 0}
                                aria-disabled={isCalling ? "true" : "false"}
                            >
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
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </ThemeProvider>
    )
}

export default MainPage