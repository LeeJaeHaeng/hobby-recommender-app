import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  CircularProgress,
  Chip,
  Alert,
} from '@mui/material';
import { EmojiEvents, ArrowForward } from '@mui/icons-material';

function RecommendationsPage() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      // localStorage에서 설문 결과 가져오기
      const surveyData = JSON.parse(localStorage.getItem('survey_responses') || '{}');

      if (!surveyData.indoor_outdoor) {
        setError('먼저 설문에 응답해주세요.');
        setLoading(false);
        return;
      }

      // 임시 추천 데이터 (추후 백엔드 연동)
      const tempRecommendations = [
        {
          id: 1,
          name: '요가',
          category: '운동',
          description: '몸과 마음의 균형을 찾는 건강한 운동입니다. 집에서도 쉽게 시작할 수 있고, 나이에 관계없이 누구나 즐길 수 있습니다.',
          match_score: 95,
          difficulty: '쉬움',
          budget: '3만원 이하',
        },
        {
          id: 2,
          name: '수채화',
          category: '예술',
          description: '물과 색의 조화로 아름다운 그림을 그려보세요. 창의력을 발휘하며 마음의 평화를 찾을 수 있습니다.',
          match_score: 88,
          difficulty: '보통',
          budget: '3만원~10만원',
        },
        {
          id: 3,
          name: '정원 가꾸기',
          category: '정원',
          description: '식물을 키우며 자연과 함께하는 시간을 가져보세요. 매일 조금씩 성장하는 식물을 보며 보람을 느낄 수 있습니다.',
          match_score: 82,
          difficulty: '쉬움',
          budget: '3만원~10만원',
        }
      ];

      setRecommendations(tempRecommendations);
    } catch (err) {
      setError('추천 취미를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetail = (hobbyId) => {
    navigate(`/hobbies/${hobbyId}`);
  };

  const handleSurvey = () => {
    navigate('/survey');
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 6 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 6 }}>
        <Alert severity="warning" sx={{ mb: 3, fontSize: '1.2rem', p: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          onClick={handleSurvey}
          size="large"
          sx={{ px: 5, py: 2, fontSize: '1.3rem' }}
        >
          설문 시작하기
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <EmojiEvents sx={{ fontSize: 80, color: 'primary.main', mb: 3 }} />
        <Typography
          variant="h3"
          gutterBottom
          sx={{ fontWeight: 700, fontSize: '2.5rem', mb: 2 }}
        >
          추천 취미
        </Typography>
        <Typography
          variant="h6"
          color="text.secondary"
          sx={{ fontSize: '1.3rem', lineHeight: 1.6 }}
        >
          회원님께 잘 맞는 취미 {recommendations.length}가지를 추천해드려요
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {recommendations.map((hobby, index) => (
          <Card
            key={hobby.id}
            elevation={4}
            sx={{
              position: 'relative',
              border: index === 0 ? '3px solid' : '2px solid',
              borderColor: index === 0 ? 'primary.main' : 'grey.300',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6,
              },
            }}
          >
            {/* 순위 뱃지 */}
            <Box
              sx={{
                position: 'absolute',
                top: -12,
                left: 20,
                bgcolor: index === 0 ? 'warning.main' : index === 1 ? 'primary.light' : 'primary.main',
                color: 'white',
                borderRadius: '50%',
                width: 60,
                height: 60,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                fontSize: '1.8rem',
                boxShadow: 3,
                zIndex: 1,
              }}
            >
              {index + 1}
            </Box>

            <CardContent sx={{ pt: 5, px: 4, pb: 4 }}>
              {/* 제목과 카테고리 */}
              <Typography
                variant="h4"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  fontSize: '2rem',
                  mb: 2,
                  color: 'text.primary',
                }}
              >
                {hobby.name}
              </Typography>

              <Box sx={{ mb: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={hobby.category}
                  size="medium"
                  color="primary"
                  sx={{ fontSize: '1.1rem', px: 1, py: 2.5 }}
                />
                <Chip
                  label={`매칭률 ${hobby.match_score}%`}
                  size="medium"
                  color="success"
                  sx={{ fontSize: '1.1rem', px: 1, py: 2.5 }}
                />
              </Box>

              {/* 설명 */}
              <Typography
                variant="body1"
                paragraph
                sx={{
                  fontSize: '1.2rem',
                  lineHeight: 1.8,
                  mb: 3,
                  color: 'text.primary',
                }}
              >
                {hobby.description}
              </Typography>

              {/* 난이도와 예산 */}
              <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Box>
                  <Typography
                    variant="body2"
                    sx={{ fontSize: '1rem', color: 'text.secondary', mb: 0.5 }}
                  >
                    난이도
                  </Typography>
                  <Typography variant="h6" sx={{ fontSize: '1.2rem', fontWeight: 600 }}>
                    {hobby.difficulty}
                  </Typography>
                </Box>
                <Box>
                  <Typography
                    variant="body2"
                    sx={{ fontSize: '1rem', color: 'text.secondary', mb: 0.5 }}
                  >
                    예상 비용 (월)
                  </Typography>
                  <Typography variant="h6" sx={{ fontSize: '1.2rem', fontWeight: 600 }}>
                    {hobby.budget}
                  </Typography>
                </Box>
              </Box>

              {/* 자세히 보기 버튼 */}
              <Button
                variant="contained"
                size="large"
                onClick={() => handleDetail(hobby.id)}
                endIcon={<ArrowForward />}
                sx={{
                  px: 4,
                  py: 2,
                  fontSize: '1.2rem',
                  fontWeight: 600,
                  width: '100%',
                  mt: 2,
                }}
              >
                자세히 보기
              </Button>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* 다시 하기 버튼 */}
      <Box sx={{ mt: 6, textAlign: 'center' }}>
        <Button
          variant="outlined"
          size="large"
          onClick={handleSurvey}
          sx={{ px: 5, py: 2, fontSize: '1.2rem' }}
        >
          설문 다시 하기
        </Button>
      </Box>
    </Container>
  );
}

export default RecommendationsPage;
