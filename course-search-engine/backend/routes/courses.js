// backend/routes/courses.js
const express = require('express');
const router = express.Router();
const multer = require('multer');
const pdfParse = require('pdf-parse');
const OpenAI = require('openai');
const Course = require('../models/Course');

const { extractFromPDF } = require('../controllers/pdfExtractController');

const upload = multer({ storage: multer.memoryStorage() });

// @route   POST /api/courses/extract-from-pdf
// @desc    Extract course details from uploaded PDF
router.post('/extract-from-pdf', upload.single('pdf'), extractFromPDF);

// @route   GET /api/courses/search?q=keyword
// @desc    Search courses by title or code
router.get('/search', async (req, res) => {
  try {
    const { q } = req.query;
    if (!q) {
      return res.status(400).json({ message: 'Query parameter q is required' });
    }
    const regex = new RegExp(q, 'i');
    const courses = await Course.find({
      $or: [
        { courseTitle: { $regex: regex } },
        { courseCode: { $regex: regex } }
      ]
    }).select('courseCode courseTitle credits aims');
    res.json(courses);
  } catch (error) {
    res.status(500).json({ message: 'Server Error', error: error.message });
  }
});

// @route   GET /api/courses
// @desc    Get all courses
router.get('/', async (req, res) => {
  try {
    const courses = await Course.find().select('courseCode courseTitle credits aims');
    res.json(courses);
  } catch (error) {
    res.status(500).json({ message: 'Server Error', error: error.message });
  }
});

// @route   GET /api/courses/:id
// @desc    Get single course by ID
router.get('/:id', async (req, res) => {
  try {
    const course = await Course.findById(req.params.id);
    if (!course) {
      return res.status(404).json({ message: 'Course not found' });
    }
    res.json(course);
  } catch (error) {
    res.status(500).json({ message: 'Server Error', error: error.message });
  }
});

// @route   POST /api/courses
// @desc    Add a new course
router.post('/', async (req, res) => {
  try {
    const newCourse = new Course(req.body);
    const savedCourse = await newCourse.save();
    res.status(201).json(savedCourse);
  } catch (error) {
    res.status(400).json({ message: 'Error adding course', error: error.message });
  }
});

module.exports = router;
