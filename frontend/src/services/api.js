/**
 * Backend API 호출 모듈
 *
 * 사용법:
 * import api from './services/api';
 * const patients = await api.get('/patients');
 */

import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:3000/api", // Backend 주소
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
