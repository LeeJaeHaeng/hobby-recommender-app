import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import SurveyPage from './pages/SurveyPage';
import HobbiesPage from './pages/HobbiesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import HobbyDetailPage from './pages/HobbyDetailPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // 편안한 녹색
    },
    secondary: {
      main: '#FF6F00', // 따뜻한 오렌지
    },
  },
  typography: {
    fontSize: 16, // 기본 글꼴 크기 증가
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Malgun Gothic"',
      'sans-serif',
    ].join(','),
    h4: {
      fontSize: '2rem',
      fontWeight: 700,
    },
    h5: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1.1rem',
    },
    button: {
      fontSize: '1.1rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          padding: '12px 24px',
          borderRadius: 8,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-input': {
            fontSize: '1.1rem',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/survey" element={<SurveyPage />} />
          <Route path="/hobbies" element={<HobbiesPage />} />
          <Route path="/hobbies/:id" element={<HobbyDetailPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;