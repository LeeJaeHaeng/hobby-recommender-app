import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT 토큰 관리
export const setAuthToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }
};

// 초기 로드 시 토큰 설정
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

export const api = {
  // 인증
  signup: (userData) => apiClient.post('/users/signup', userData),
  login: (credentials) => apiClient.post('/auth/login', credentials),
  logout: () => apiClient.post('/auth/logout'),

  // 설문
  getSurveyQuestions: () => apiClient.get('/survey/questions'),
  submitSurvey: (responses) => apiClient.post('/survey/submit', { responses }),

  // 취미
  getHobbies: (params) => apiClient.get('/hobbies', { params }),
  getHobbyDetail: (id) => apiClient.get(`/hobbies/${id}`),
  rateHobby: (id, ratingData) => apiClient.post(`/hobbies/${id}/rate`, ratingData),
  getCategories: () => apiClient.get('/hobbies/categories'),

  // 추천
  getRecommendations: (params) => apiClient.get('/recommendations', { params }),
  getPopularHobbies: (params) => apiClient.get('/recommendations/popular', { params }),
  getSimilarHobbies: (id, params) => apiClient.get(`/recommendations/similar/${id}`, { params }),

  // 모임
  getGatherings: (params) => apiClient.get('/gatherings', { params }),
  getGatheringDetail: (id) => apiClient.get(`/gatherings/${id}`),
  createGathering: (data) => apiClient.post('/gatherings', data),
  getRegions: () => apiClient.get('/gatherings/regions'),
};

export default apiClient;