import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  MenuItem,
  Box,
  CircularProgress,
  Chip,
  Rating,
} from '@mui/material';
import { api } from '../services/api';

function HobbiesPage() {
  const navigate = useNavigate();
  const [hobbies, setHobbies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    search: '',
    indoor_outdoor: '',
    budget: '',
  });

  useEffect(() => {
    fetchCategories();
    fetchHobbies();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.getCategories();
      setCategories(response.data.data.categories);
    } catch (err) {
      console.error('카테고리 조회 실패:', err);
    }
  };

  const fetchHobbies = async () => {
    setLoading(true);
    try {
      const response = await api.getHobbies(filters);
      setHobbies(response.data.data.hobbies);
    } catch (err) {
      console.error('취미 조회 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const handleSearch = () => {
    fetchHobbies();
  };

  const handleDetail = (hobbyId) => {
    navigate(`/hobbies/${hobbyId}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        취미 탐색
      </Typography>

      {/* 필터 */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="검색"
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="취미 이름 검색"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="카테고리"
              name="category"
              value={filters.category}
              onChange={handleFilterChange}
            >
              <MenuItem value="">전체</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat.category} value={cat.category}>
                  {cat.category} ({cat.count})
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              select
              label="실내/외"
              name="indoor_outdoor"
              value={filters.indoor_outdoor}
              onChange={handleFilterChange}
            >
              <MenuItem value="">전체</MenuItem>
              <MenuItem value="indoor">실내</MenuItem>
              <MenuItem value="outdoor">야외</MenuItem>
              <MenuItem value="both">상관없음</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              select
              label="예산"
              name="budget"
              value={filters.budget}
              onChange={handleFilterChange}
            >
              <MenuItem value="">전체</MenuItem>
              <MenuItem value="low">저렴</MenuItem>
              <MenuItem value="medium">보통</MenuItem>
              <MenuItem value="high">고가</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              sx={{ height: '56px' }}
            >
              검색
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* 취미 목록 */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {hobbies.map((hobby) => (
            <Grid item xs={12} sm={6} md={4} key={hobby.hobby_id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {hobby.name}
                  </Typography>

                  <Box sx={{ mb: 1 }}>
                    <Chip label={hobby.category} size="small" color="primary" />
                    <Chip
                      label={hobby.indoor_outdoor}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                    <Chip
                      label={hobby.required_budget}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {hobby.description}
                  </Typography>

                  <Box sx={{ mt: 2 }}>
                    <Rating
                      value={hobby.average_rating || 0}
                      readOnly
                      precision={0.5}
                      size="small"
                    />
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      ({hobby.rating_count}명 평가)
                    </Typography>
                  </Box>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    onClick={() => handleDetail(hobby.hobby_id)}
                  >
                    자세히 보기
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {!loading && hobbies.length === 0 && (
        <Typography variant="body1" align="center" sx={{ mt: 4 }}>
          검색 결과가 없습니다.
        </Typography>
      )}
    </Container>
  );
}

export default HobbiesPage;
