// frontend/src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api/courses';

export const searchCourses = async (query) => {
  const response = await axios.get(`${API_URL}/search?q=${query}`);
  return response.data;
};

export const getCourseDetails = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const getAllCourses = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const extractCourseFromPdf = async (file) => {
  const formData = new FormData();
  formData.append('pdf', file);
  
  const response = await axios.post(`${API_URL}/extract-from-pdf`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const createCourse = async (courseData) => {
  const response = await axios.post(API_URL, courseData);
  return response.data;
};

export const importCoursesFromCsv = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post('http://localhost:5000/api/import/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};
