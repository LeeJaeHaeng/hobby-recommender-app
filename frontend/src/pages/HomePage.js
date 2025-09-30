import React from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box 
        display="flex" 
        flexDirection="column" 
        alignItems="center" 
        justifyContent="center" 
        minHeight="100vh"
        textAlign="center"
      >
        <Typography variant="h2" component="h1" gutterBottom>
          퇴직자 맞춤 취미 추천
        </Typography>
        <Typography variant="h5" color="textSecondary" paragraph>
          새로운 인생 2막을 위한 완벽한 취미를 찾아보세요
        </Typography>
        <Button 
          variant="contained" 
          size="large" 
          onClick={() => navigate('/survey')}
          sx={{ mt: 3, mb: 2, px: 4, py: 2 }}
        >
          취미 찾기 시작하기
        </Button>
      </Box>
    </Container>
  );
};

export default HomePage;