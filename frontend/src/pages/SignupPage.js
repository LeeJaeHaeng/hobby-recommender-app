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
  MenuItem,
  Grid,
} from '@mui/material';
import { api } from '../services/api';

function SignupPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    birth_year: '',
    gender: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 80 }, (_, i) => currentYear - 20 - i);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return false;
    }

    if (formData.password.length < 8) {
      setError('비밀번호는 최소 8자 이상이어야 합니다.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setLoading(true);

    try {
      const { confirmPassword, ...signupData } = formData;
      await api.signup({
        ...signupData,
        birth_year: parseInt(signupData.birth_year),
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.message || '회원가입에 실패했습니다.');
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
            회원가입
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, fontSize: '1.1rem', p: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 3, fontSize: '1.1rem', p: 2 }}>
              회원가입이 완료되었습니다! 로그인 페이지로 이동합니다...
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="이름"
              name="name"
              value={formData.name}
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
              label="사용자명"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              helperText="영문, 숫자 조합 4-20자"
              sx={{
                mb: 2,
                '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
                '& .MuiFormHelperText-root': { fontSize: '1rem' },
              }}
            />

            <TextField
              fullWidth
              label="이메일"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 2,
                '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
              }}
            />

            <Grid container spacing={2} sx={{ mt: 1, mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  select
                  label="출생연도"
                  name="birth_year"
                  value={formData.birth_year}
                  onChange={handleChange}
                  required
                  sx={{
                    '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                    '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
                  }}
                >
                  {years.map((year) => (
                    <MenuItem key={year} value={year} sx={{ fontSize: '1.1rem' }}>
                      {year}년
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={6}>
                <TextField
                  fullWidth
                  select
                  label="성별"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  required
                  sx={{
                    '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                    '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
                  }}
                >
                  <MenuItem value="male" sx={{ fontSize: '1.1rem' }}>
                    남성
                  </MenuItem>
                  <MenuItem value="female" sx={{ fontSize: '1.1rem' }}>
                    여성
                  </MenuItem>
                  <MenuItem value="other" sx={{ fontSize: '1.1rem' }}>
                    기타
                  </MenuItem>
                </TextField>
              </Grid>
            </Grid>

            <TextField
              fullWidth
              label="비밀번호"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              helperText="최소 8자 이상"
              sx={{
                mb: 2,
                '& .MuiInputLabel-root': { fontSize: '1.2rem' },
                '& .MuiInputBase-input': { fontSize: '1.2rem', py: 2 },
                '& .MuiFormHelperText-root': { fontSize: '1rem' },
              }}
            />

            <TextField
              fullWidth
              label="비밀번호 확인"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
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
              disabled={loading || success}
            >
              {loading ? <CircularProgress size={28} color="inherit" /> : '회원가입'}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body1" sx={{ fontSize: '1.1rem' }}>
                이미 계정이 있으신가요?{' '}
                <Link
                  to="/login"
                  style={{
                    textDecoration: 'none',
                    color: '#2E7D32',
                    fontWeight: 600,
                  }}
                >
                  로그인
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

export default SignupPage;
