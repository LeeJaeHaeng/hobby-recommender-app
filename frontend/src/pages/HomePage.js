import React, { useEffect, useState } from 'react';
import { Container, Typography, Button, Box, Grid, Card, CardContent, AppBar, Toolbar } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { EmojiEvents, Search, Group, Logout } from '@mui/icons-material';

const HomePage = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
      setIsLoggedIn(true);
      setUserName(JSON.parse(user).username);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    window.location.reload();
  };

  return (
    <Box>
      {/* 상단 네비게이션 */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer', fontWeight: 700 }} onClick={() => navigate('/')}>
            🌱 휴라이프
          </Typography>
          {isLoggedIn ? (
            <>
              <Typography variant="body1" sx={{ mr: 2 }}>
                {userName}님
              </Typography>
              <Button color="inherit" onClick={() => navigate('/hobbies')}>
                취미 탐색
              </Button>
              <Button color="inherit" onClick={() => navigate('/recommendations')}>
                맞춤 추천
              </Button>
              <Button color="inherit" onClick={handleLogout} startIcon={<Logout />}>
                로그아웃
              </Button>
            </>
          ) : (
            <>
              <Button color="inherit" onClick={() => navigate('/login')}>
                로그인
              </Button>
              <Button color="inherit" onClick={() => navigate('/signup')}>
                회원가입
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      {/* 메인 콘텐츠 */}
      <Container maxWidth="lg">
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="60vh"
          textAlign="center"
          py={8}
        >
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" sx={{ color: 'primary.main' }}>
            🌱 휴라이프
          </Typography>
          <Typography variant="h4" color="textSecondary" paragraph sx={{ maxWidth: 700, lineHeight: 1.6 }}>
            나에게 꼭 맞는 취미를 쉽고 간단하게 찾아보세요
          </Typography>

          {isLoggedIn ? (
            <Box sx={{ mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/survey')}
                sx={{ mr: 2, px: 5, py: 2.5, fontSize: '1.3rem' }}
              >
                내 취미 찾기
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/hobbies')}
                sx={{ px: 5, py: 2.5, fontSize: '1.3rem' }}
              >
                취미 둘러보기
              </Button>
            </Box>
          ) : (
            <Box sx={{ mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/signup')}
                sx={{ mr: 2, px: 4, py: 2 }}
              >
                시작하기
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/login')}
                sx={{ px: 4, py: 2 }}
              >
                로그인
              </Button>
            </Box>
          )}
        </Box>

        {/* 기능 소개 */}
        <Grid container spacing={4} sx={{ mb: 8 }}>
          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <EmojiEvents sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  나만의 취미 추천
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  간단한 질문으로 나에게 딱 맞는 취미를 찾아드립니다
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Search sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  다양한 취미
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  운동, 예술, 음악 등 다양한 카테고리의 취미를 탐색하세요
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Group sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  모임 찾기
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  지역별 취미 모임을 찾아 함께 즐기세요
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default HomePage;