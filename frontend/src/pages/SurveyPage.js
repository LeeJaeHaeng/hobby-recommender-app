import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const SurveyPage = () => {
  return (
    <Container maxWidth="md">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          성향 분석 설문
        </Typography>
        <Paper elevation={3} sx={{ p: 4, mt: 3 }}>
          <Typography variant="body1">
            설문조사 컴포넌트가 여기에 들어갑니다.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default SurveyPage;