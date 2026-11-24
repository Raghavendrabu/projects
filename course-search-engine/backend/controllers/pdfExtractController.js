// backend/controllers/pdfExtractController.js
const pdfParse = require('pdf-parse');

const extractFromPDF = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, message: 'No PDF file uploaded' });
    }

    // Extract text from PDF
    const pdfData = await pdfParse(req.file.buffer);
    const extractedText = pdfData.text;
    
    // Extract Course Code
    const courseCodeMatch = extractedText.match(/Course Code\s*([A-Z0-9]+)/);
    const courseCode = courseCodeMatch ? courseCodeMatch[1] : '';
    
    // Extract Course Title
    const courseTitleMatch = extractedText.match(/Course Title\s*(.+?)(?=Program Code|$)/);
    const courseTitle = courseTitleMatch ? courseTitleMatch[1].trim() : '';
    
    // Extract Credits
    const creditsMatch = extractedText.match(/Credits\s*(\d+)/);
    const credits = creditsMatch ? parseInt(creditsMatch[1]) : 3;
    
    // Extract Aims (text between "Course Aims and Summary" and "Course Objectives")
    const aimsMatch = extractedText.match(/Course Aims and Summary\s*(.*?)(?=Course Objectives|$)/s);
    const aims = aimsMatch ? aimsMatch[1].trim() : '';
    
    // Extract ALL Objectives (numbered 1. 2. 3. ... up to 10)
    const objectivesSection = extractedText.match(/Course Objectives(.*?)(?=Course Outcomes|$)/s);
    const objectives = [];
    if (objectivesSection) {
      const objectiveMatches = objectivesSection[1].match(/(\d+)\.\s*([^.\d][^.\n]*?)(?=\d+\.|$)/gs);
      if (objectiveMatches) {
        objectiveMatches.forEach(match => {
          const text = match.replace(/^\d+\.\s*/, '').trim();
          if (text) objectives.push(text);
        });
      }
    }
    
    // Extract Outcomes (CO1, CO2, etc.)
    const outcomesSection = extractedText.match(/Course Outcomes(.*?)(?=Course Content|UNIT|$)/s);
    const outcomes = [];
    if (outcomesSection) {
      const outcomeMatches = outcomesSection[1].match(/CO(\d+):\s*([^.\n][^.\n]*)/g);
      if (outcomeMatches) {
        outcomeMatches.forEach(match => {
          const codeMatch = match.match(/(CO\d+):\s*(.*)/);
          if (codeMatch) {
            outcomes.push({ code: codeMatch[1], description: codeMatch[2].trim() });
          }
        });
      }
    }
    
    // Extract Units (Unit I to Unit V)
    const units = [];
    const unitPatterns = [
      { num: 'I', title: 'FOUNDATIONS OF IMMERSIVE TECHNOLOGIES', next: 'II' },
      { num: 'II', title: 'HARDWARE AND RENDERING FOR IMMERSIVE SYSTEMS', next: 'III' },
      { num: 'III', title: '3D MATHEMATICS AND SPATIAL COMPUTING', next: 'IV' },
      { num: 'IV', title: 'AR/VR DEVELOPMENT AND INTERACTION', next: 'V' },
      { num: 'V', title: 'METAVERSE, ECONOMICS AND FUTURE DIRECTIONS', next: 'Text Books' }
    ];
    
    for (const unit of unitPatterns) {
      const nextPattern = unit.next === 'Text Books' ? 'Text Books' : `UNIT ${unit.next}`;
      const unitRegex = new RegExp(`UNIT ${unit.num} - ${unit.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(.*?)(?=${nextPattern}|$)`, 'is');
      const unitMatch = extractedText.match(unitRegex);
      if (unitMatch) {
        const unitText = unitMatch[1];
        const topics = unitText.split(/\n/)
          .filter(line => line.trim().match(/^[-•*]\s+/) || line.trim().match(/^\d+\.\s+/))
          .map(line => line.trim().replace(/^[-•*\d+\.\s]+/, '').trim())
          .filter(topic => topic.length > 0);
        
        units.push({
          unitNumber: unit.num,
          title: unit.title,
          topics: topics.length ? topics : [unitText.substring(0, 500).trim()]
        });
      }
    }
    
    // Extract Textbooks
    const textbooksMatch = extractedText.match(/Text Books\s*(.*?)(?=References|$)/is);
    const textbooks = [];
    if (textbooksMatch) {
      const textbookLines = textbooksMatch[1].split(/\d+\./);
      textbookLines.forEach(line => {
        const clean = line.trim();
        if (clean && !clean.includes('Text Books')) {
          textbooks.push(clean);
        }
      });
    }
    
    // Extract Assessment
    const quizMatch = extractedText.match(/Quiz\s*(\d+)/i);
    const testMatch = extractedText.match(/Test\s*(\d+)/i);
    const assignmentMatch = extractedText.match(/Assignment\s*(\d+)/i);
    const seeMatch = extractedText.match(/SEE\s*(\d+)/i);
    
    const assessment = {
      quiz: quizMatch ? parseInt(quizMatch[1]) : 15,
      test: testMatch ? parseInt(testMatch[1]) : 25,
      assignment: assignmentMatch ? parseInt(assignmentMatch[1]) : 20,
      see: seeMatch ? parseInt(seeMatch[1]) : 40,
      total: 100
    };
    
    // Extract Grading
    const grading = [];
    const gradingSection = extractedText.match(/Grading Criterion(.*?)(?=Practical|$)/is);
    if (gradingSection) {
      const gradeMatches = gradingSection[1].match(/(\d+)\s*(?:and above|-?\s*(\d+))\s*-\s*([^-]+)/g);
      if (gradeMatches) {
        gradeMatches.forEach(match => {
          const rangeMatch = match.match(/(\d+)(?:\s*and above\s*|\s*-\s*(\d+)\s*)-?\s*(.+)/);
          if (rangeMatch) {
            grading.push({
              range: rangeMatch[2] ? `${rangeMatch[1]}-${rangeMatch[2]}` : `${rangeMatch[1]}+`,
              grade: rangeMatch[3].trim().split(' ')[0],
              description: rangeMatch[3].trim()
            });
          }
        });
      }
    }
    
    const extractedData = {
      courseCode,
      courseTitle,
      credits,
      ltp: "3-0-0",
      hoursPerWeek: 3,
      aims,
      objectives,
      outcomes,
      syllabusUnits: units,
      assessment,
      textbooks,
      grading
    };
    
    res.json({ success: true, ...extractedData });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

module.exports = { extractFromPDF };
