import './styles.css';
import { useNavigate } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

const theme = createTheme({
    palette: {
        primary: {
            main: '#7394EE',
        },
    },
});

export default function NotFoundPage() {
    const navigate = useNavigate();

    return (
        <ThemeProvider theme={theme}>
            <Stack
                direction="row"
                justifyContent="center"
                alignItems="center"
                sx={{ height: "100vh" }}
            >
                <Box className="not-found-container">
                    <p className="title">Страница не найдена</p>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => navigate(-1)}
                    >Вернуться</Button>
                </Box>
            </Stack>
        </ThemeProvider>
    )
}
