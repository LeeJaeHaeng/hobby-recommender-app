import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { api, setAuthToken } from '../services/api';

function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.login(formData);
      const { access_token, user } = response.data.data;

      // 토큰 저장
      setAuthToken(access_token);
      localStorage.setItem('user', JSON.stringify(user));

      // 메인 페이지로 이동
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || '로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 8 }}>
        {/* 로고 */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h3"
            sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}
          >
            🌱 휴라이프
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ fontSize: '1.2rem' }}>
            나에게 맞는 취미 찾기
          </Typography>
        </Box>

        <Paper elevation={4} sx={{ p: 5 }}>
          <Typography
            variant="h4"
            align="center"
            gutterBottom
            sx={{ fontWeight: 600, fontSize: '2rem', mb: 4 }}
          >
            로그인
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, fontSize: '1.1rem', p: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="사용자명"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 2,
                '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
              }}
            />

            <TextField
              fullWidth
              label="비밀번호"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 2,
                '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              sx={{ mt: 4, mb: 3, py: 2, fontSize: '1.3rem', fontWeight: 600 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={28} color="inherit" /> : '로그인'}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body1" sx={{ fontSize: '1.1rem' }}>
                계정이 없으신가요?{' '}
                <Link
                  to="/signup"
                  style={{
                    textDecoration: 'none',
                    color: '#2E7D32',
                    fontWeight: 600,
                  }}
                >
                  회원가입
                </Link>
              </Typography>
            </Box>
          </form>
        </Paper>

        {/* 홈으로 돌아가기 */}
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Button
            variant="text"
            onClick={() => navigate('/')}
            sx={{ fontSize: '1.1rem' }}
          >
            홈으로 돌아가기
          </Button>
        </Box>
      </Box>
    </Container>
  );
}

export default LoginPage;
