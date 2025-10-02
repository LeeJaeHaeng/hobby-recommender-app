import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  FavoriteBorder,
  Info,
  ShoppingCart,
} from '@mui/icons-material';

function HobbyDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [hobby, setHobby] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHobbyDetail();
  }, [id]);

  const loadHobbyDetail = async () => {
    try {
      // 임시 데이터 (추후 백엔드 연동)
      const tempHobbies = {
        1: {
          id: 1,
          name: '요가',
          category: '운동',
          description: '몸과 마음의 균형을 찾는 건강한 운동입니다. 집에서도 쉽게 시작할 수 있고, 나이에 관계없이 누구나 즐길 수 있습니다.',
          difficulty: '쉬움',
          budget: '3만원 이하',
          materials: [
            '요가 매트 (1~3만원)',
            '편안한 운동복',
            '물병',
            '수건 (선택사항)',
          ],
          benefits: [
            '유연성이 좋아집니다',
            '스트레스가 줄어듭니다',
            '균형 감각이 향상됩니다',
            '허리와 관절 통증이 완화됩니다',
            '숙면에 도움이 됩니다',
          ],
          youtubeUrl: 'https://www.youtube.com/embed/v7AYKMP6rOE',
        },
        2: {
          id: 2,
          name: '수채화',
          category: '예술',
          description: '물과 색의 조화로 아름다운 그림을 그려보세요. 창의력을 발휘하며 마음의 평화를 찾을 수 있습니다.',
          difficulty: '보통',
          budget: '3만원~10만원',
          materials: [
            '수채화 물감 세트 (2~5만원)',
            '수채화 붓 세트 (1~3만원)',
            '수채화 종이 (1~2만원)',
            '물통과 팔레트',
          ],
          benefits: [
            '창의력이 발달합니다',
            '집중력이 향상됩니다',
            '감정 표현이 자유로워집니다',
            '성취감을 느낄 수 있습니다',
            '마음이 편안해집니다',
          ],
          youtubeUrl: 'https://www.youtube.com/embed/ZfKUwHOJYw0',
        },
        3: {
          id: 3,
          name: '정원 가꾸기',
          category: '정원',
          description: '식물을 키우며 자연과 함께하는 시간을 가져보세요. 매일 조금씩 성장하는 식물을 보며 보람을 느낄 수 있습니다.',
          difficulty: '쉬움',
          budget: '3만원~10만원',
          materials: [
            '화분 여러 개 (개당 1~2만원)',
            '흙과 비료 (2~3만원)',
            '모종이나 씨앗 (1~5만원)',
            '삽과 물뿌리개',
          ],
          benefits: [
            '자연과 함께하는 시간을 가질 수 있습니다',
            '신선한 공기를 마실 수 있습니다',
            '식물 성장을 보며 보람을 느낍니다',
            '가벼운 운동 효과가 있습니다',
            '스트레스가 해소됩니다',
          ],
          youtubeUrl: 'https://www.youtube.com/embed/lW_WQa58BZE',
        },
      };

      const hobbyData = tempHobbies[id];
      if (!hobbyData) {
        setError('취미 정보를 찾을 수 없습니다.');
      } else {
        setHobby(hobbyData);
      }
    } catch (err) {
      setError('취미 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
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

  if (error || !hobby) {
    return (
      <Container maxWidth="md" sx={{ mt: 6 }}>
        <Alert severity="error" sx={{ mb: 3, fontSize: '1.2rem', p: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBack />}
          onClick={() => navigate('/recommendations')}
          sx={{ px: 4, py: 2, fontSize: '1.2rem' }}
        >
          돌아가기
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      {/* 뒤로 가기 버튼 */}
      <Button
        variant="outlined"
        startIcon={<ArrowBack />}
        onClick={() => navigate('/recommendations')}
        sx={{ mb: 4, px: 3, py: 1.5, fontSize: '1.1rem' }}
      >
        돌아가기
      </Button>

      {/* 취미 제목 */}
      <Typography
        variant="h3"
        gutterBottom
        sx={{ fontWeight: 700, fontSize: '2.5rem', mb: 3 }}
      >
        {hobby.name}
      </Typography>

      {/* 카테고리와 난이도 */}
      <Box sx={{ mb: 4, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Chip
          label={hobby.category}
          color="primary"
          sx={{ fontSize: '1.2rem', px: 2, py: 3 }}
        />
        <Chip
          label={`난이도: ${hobby.difficulty}`}
          sx={{ fontSize: '1.2rem', px: 2, py: 3 }}
        />
        <Chip
          label={`예상 비용: ${hobby.budget}`}
          sx={{ fontSize: '1.2rem', px: 2, py: 3 }}
        />
      </Box>

      {/* 설명 */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Info sx={{ fontSize: 32, color: 'primary.main', mr: 1 }} />
          <Typography variant="h5" sx={{ fontWeight: 600, fontSize: '1.8rem' }}>
            이런 취미예요
          </Typography>
        </Box>
        <Typography
          variant="body1"
          sx={{ fontSize: '1.3rem', lineHeight: 1.8, color: 'text.primary' }}
        >
          {hobby.description}
        </Typography>
      </Paper>

      {/* 필요한 준비물 */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <ShoppingCart sx={{ fontSize: 32, color: 'primary.main', mr: 1 }} />
          <Typography variant="h5" sx={{ fontWeight: 600, fontSize: '1.8rem' }}>
            필요한 준비물
          </Typography>
        </Box>
        <List>
          {hobby.materials.map((material, index) => (
            <ListItem key={index} sx={{ px: 0, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <CheckCircle sx={{ color: 'success.main', fontSize: 28 }} />
              </ListItemIcon>
              <ListItemText
                primary={material}
                primaryTypographyProps={{
                  fontSize: '1.3rem',
                  fontWeight: 500,
                }}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* 기대 효과 */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <FavoriteBorder sx={{ fontSize: 32, color: 'primary.main', mr: 1 }} />
          <Typography variant="h5" sx={{ fontWeight: 600, fontSize: '1.8rem' }}>
            이런 점이 좋아요
          </Typography>
        </Box>
        <List>
          {hobby.benefits.map((benefit, index) => (
            <ListItem key={index} sx={{ px: 0, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <CheckCircle sx={{ color: 'primary.main', fontSize: 28 }} />
              </ListItemIcon>
              <ListItemText
                primary={benefit}
                primaryTypographyProps={{
                  fontSize: '1.3rem',
                  fontWeight: 500,
                }}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* 유튜브 영상 */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography
          variant="h5"
          gutterBottom
          sx={{ fontWeight: 600, fontSize: '1.8rem', mb: 3 }}
        >
          시작하는 방법 (영상으로 보기)
        </Typography>
        <Box
          sx={{
            position: 'relative',
            paddingBottom: '56.25%', // 16:9 비율
            height: 0,
            overflow: 'hidden',
            borderRadius: 2,
          }}
        >
          <iframe
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              border: 'none',
              borderRadius: 8,
            }}
            src={hobby.youtubeUrl}
            title={`${hobby.name} 튜토리얼`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </Box>
        <Typography
          variant="body2"
          sx={{ mt: 2, fontSize: '1.1rem', color: 'text.secondary' }}
        >
          영상을 보시면서 천천히 따라해보세요
        </Typography>
      </Paper>

      {/* 돌아가기 버튼 (하단) */}
      <Box sx={{ mt: 5, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/recommendations')}
          sx={{ px: 6, py: 2.5, fontSize: '1.3rem', fontWeight: 600 }}
        >
          다른 추천 보기
        </Button>
      </Box>
    </Container>
  );
}

export default HobbyDetailPage;
