import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import { api } from '../services/api';

const SurveyPage = () => {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [responses, setResponses] = useState({});

  // 간단하고 명확한 5개 질문
  const questions = [
    {
      id: 1,
      text: '집 안에서 하는 활동과 밖에서 하는 활동 중 어떤 것을 더 좋아하시나요?',
      type: 'choice',
      options: [
        { value: 'indoor', label: '집 안에서 조용히 하는 활동' },
        { value: 'outdoor', label: '밖에 나가서 하는 활동' },
        { value: 'both', label: '둘 다 괜찮아요' }
      ]
    },
    {
      id: 2,
      text: '혼자 하는 취미와 다른 사람들과 함께 하는 취미 중 어떤 것을 선호하시나요?',
      type: 'choice',
      options: [
        { value: 'alone', label: '혼자서 조용히 하는 게 좋아요' },
        { value: 'together', label: '사람들과 함께 하는 게 좋아요' },
        { value: 'both', label: '둘 다 괜찮아요' }
      ]
    },
    {
      id: 3,
      text: '몸을 많이 움직이는 활동을 하시는 것을 좋아하시나요?',
      type: 'choice',
      options: [
        { value: 'yes', label: '네, 운동이나 활동적인 것을 좋아해요' },
        { value: 'moderate', label: '가볍게 움직이는 정도가 좋아요' },
        { value: 'no', label: '아니요, 조용한 활동이 더 좋아요' }
      ]
    },
    {
      id: 4,
      text: '무언가를 만들거나 그리는 것을 좋아하시나요?',
      type: 'choice',
      options: [
        { value: 'yes', label: '네, 손으로 만드는 것을 좋아해요' },
        { value: 'no', label: '아니요, 다른 활동이 더 좋아요' },
        { value: 'maybe', label: '한 번 해보고 싶어요' }
      ]
    },
    {
      id: 5,
      text: '취미 활동에 한 달에 얼마 정도 쓰실 수 있으신가요?',
      type: 'choice',
      options: [
        { value: 'low', label: '3만원 이하' },
        { value: 'medium', label: '3만원~10만원' },
        { value: 'high', label: '10만원 이상' }
      ]
    }
  ];

  const handleAnswer = (questionId, value) => {
    setResponses({
      ...responses,
      [questionId]: value,
    });
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');

    try {
      // 간단한 형태로 서버에 전달 (백엔드에서 처리)
      const surveyData = {
        indoor_outdoor: responses[1],
        social_preference: responses[2],
        physical_activity: responses[3],
        creative_interest: responses[4],
        budget: responses[5]
      };

      // 임시로 localStorage에 저장 (추후 백엔드 연동)
      localStorage.setItem('survey_responses', JSON.stringify(surveyData));

      navigate('/recommendations');
    } catch (err) {
      setError('설문 제출에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setSubmitting(false);
    }
  };

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;
  const isAnswered = responses[currentQuestion.id] !== undefined;
  const allAnswered = questions.every((q) => responses[q.id] !== undefined);

  return (
    <Container maxWidth="md">
      <Box py={6}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          align="center"
          sx={{ fontWeight: 700, fontSize: '2.2rem', mb: 4 }}
        >
          나에게 맞는 취미 찾기
        </Typography>

        <Box sx={{ mb: 4 }}>
          <Typography
            variant="h6"
            align="center"
            gutterBottom
            sx={{ fontSize: '1.4rem', fontWeight: 600 }}
          >
            {currentIndex + 1} / {questions.length}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3, fontSize: '1.1rem' }}>
            {error}
          </Alert>
        )}

        <Paper elevation={3} sx={{ p: 5, mt: 4 }}>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend" sx={{ mb: 4 }}>
              <Typography
                variant="h5"
                sx={{
                  fontSize: '1.5rem',
                  fontWeight: 600,
                  lineHeight: 1.6,
                  color: 'text.primary'
                }}
              >
                {currentQuestion.text}
              </Typography>
            </FormLabel>

            <RadioGroup
              value={responses[currentQuestion.id] || ''}
              onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
            >
              {currentQuestion.options.map((option) => (
                <FormControlLabel
                  key={option.value}
                  value={option.value}
                  control={<Radio size="large" />}
                  label={option.label}
                  sx={{
                    mb: 2,
                    p: 2,
                    borderRadius: 2,
                    border: '2px solid',
                    borderColor: responses[currentQuestion.id] === option.value
                      ? 'primary.main'
                      : 'grey.300',
                    backgroundColor: responses[currentQuestion.id] === option.value
                      ? 'primary.light'
                      : 'transparent',
                    '& .MuiFormControlLabel-label': {
                      fontSize: '1.2rem',
                      fontWeight: 500
                    }
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 5 }}>
            <Button
              variant="outlined"
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              sx={{ px: 4, py: 2, fontSize: '1.2rem' }}
            >
              이전
            </Button>

            {currentIndex < questions.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!isAnswered}
                sx={{ px: 4, py: 2, fontSize: '1.2rem' }}
              >
                다음
              </Button>
            ) : (
              <Button
                variant="contained"
                color="success"
                onClick={handleSubmit}
                disabled={!allAnswered || submitting}
                sx={{ px: 5, py: 2, fontSize: '1.2rem', fontWeight: 700 }}
              >
                {submitting ? <CircularProgress size={24} color="inherit" /> : '완료'}
              </Button>
            )}
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SurveyPage;