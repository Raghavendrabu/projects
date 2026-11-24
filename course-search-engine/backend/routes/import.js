// backend/routes/import.js
const express = require('express');
const router = express.Router();
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const Course = require('../models/Course');

const upload = multer({ dest: 'uploads/' });

// @route   POST /api/import/csv
// @desc    Import courses from CSV
router.post('/csv', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'No file uploaded' });
  }

  const courses = [];
  fs.createReadStream(req.file.path)
    .pipe(csv())
    .on('data', (row) => {
      // Transform flat CSV row to structured Course object
      try {
        const course = {
          courseCode: row.courseCode,
          courseTitle: row.courseTitle,
          credits: parseInt(row.credits),
          ltp: row.ltp,
          aims: row.aims,
          objectives: row.objectives ? row.objectives.split('|').map(o => o.trim()) : [],
          outcomes: row.outcomes ? row.outcomes.split('|').map(o => {
            const [code, ...desc] = o.split(':');
            return { code: code.trim(), description: desc.join(':').trim() };
          }) : [],
          syllabusUnits: [
            { unitNumber: "I", title: row.unit1 ? row.unit1.split(':')[0].replace('UNIT I - ', '').trim() : "UNIT I", topics: row.unit1 ? row.unit1.split(':')[1]?.split(',').map(t => t.trim()) : [] },
            { unitNumber: "II", title: row.unit2 ? row.unit2.split(':')[0].replace('UNIT II - ', '').trim() : "UNIT II", topics: row.unit2 ? row.unit2.split(':')[1]?.split(',').map(t => t.trim()) : [] },
            { unitNumber: "III", title: row.unit3 ? row.unit3.split(':')[0].replace('UNIT III - ', '').trim() : "UNIT III", topics: row.unit3 ? row.unit3.split(':')[1]?.split(',').map(t => t.trim()) : [] },
            { unitNumber: "IV", title: row.unit4 ? row.unit4.split(':')[0].replace('UNIT IV - ', '').trim() : "UNIT IV", topics: row.unit4 ? row.unit4.split(':')[1]?.split(',').map(t => t.trim()) : [] },
            { unitNumber: "V", title: row.unit5 ? row.unit5.split(':')[0].replace('UNIT V - ', '').trim() : "UNIT V", topics: row.unit5 ? row.unit5.split(':')[1]?.split(',').map(t => t.trim()) : [] }
          ],
          assessment: {
            quiz: parseInt(row.assessmentQuiz) || 15,
            test: parseInt(row.assessmentTest) || 25,
            assignment: parseInt(row.assessmentAssignment) || 20,
            see: parseInt(row.assessmentSEE) || 40,
            total: 100
          },
          textbooks: row.textbooks ? row.textbooks.split('|').map(t => t.trim()) : [],
          grading: row.grading ? row.grading.split('|').map(g => {
            const [range, ...gradeInfo] = g.split(':');
            const gradeText = gradeInfo.join(':').trim();
            const grade = gradeText.split(' ')[0];
            return { range: range.trim(), grade: grade, description: gradeText };
          }) : []
        };
        courses.push(course);
      } catch (err) {
        console.error('Error parsing row:', err);
      }
    })
    .on('end', async () => {
      try {
        // Bulk insert or replace
        for (const courseData of courses) {
          await Course.findOneAndUpdate(
            { courseCode: courseData.courseCode },
            courseData,
            { upsert: true, new: true }
          );
        }
        
        // Delete temp file
        fs.unlinkSync(req.file.path);
        
        res.json({ message: `Successfully imported ${courses.length} courses` });
      } catch (error) {
        console.error('Import error:', error);
        res.status(500).json({ message: 'Error saving courses to database', error: error.message });
      }
    });
});

module.exports = router;
