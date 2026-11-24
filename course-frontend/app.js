// Initial Data
let courses = [
    {
        id: '1',
        code: 'UE25CS3501',
        title: 'Deep Learning',
        semester: '5',
        credits: '3',
        department: 'Computer Science and Engineering',
        program: 'B. Tech. Computer Science and Engineering',
        faculty: 'Faculty of Engineering and Technology'
    }
];

// DOM Elements
const coursesGrid = document.getElementById('coursesGrid');
const searchInput = document.getElementById('searchInput');
const courseStats = document.getElementById('courseStats');
const emptyState = document.getElementById('emptyState');
const addCourseBtn = document.getElementById('addCourseBtn');
const addCourseModal = document.getElementById('addCourseModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelBtn = document.getElementById('cancelBtn');
const addCourseForm = document.getElementById('addCourseForm');

// Initialize
function init() {
    renderCourses(courses);
    setupEventListeners();
}

// Event Listeners
function setupEventListeners() {
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredCourses = courses.filter(course => 
            course.code.toLowerCase().includes(searchTerm) || 
            course.title.toLowerCase().includes(searchTerm) ||
            course.department.toLowerCase().includes(searchTerm)
        );
        renderCourses(filteredCourses);
    });

    addCourseBtn.addEventListener('click', () => {
        addCourseModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Close modal on outside click
    addCourseModal.addEventListener('click', (e) => {
        if (e.target === addCourseModal) {
            closeModal();
        }
    });

    addCourseForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const newCourse = {
            id: Date.now().toString(),
            code: document.getElementById('courseCode').value,
            title: document.getElementById('courseTitle').value,
            semester: document.getElementById('semester').value,
            credits: document.getElementById('credits').value,
            department: document.getElementById('department').value,
            program: 'N/A', // Default values for newly added basic courses
            faculty: 'N/A'
        };

        courses.push(newCourse);
        renderCourses(courses);
        closeModal();
        
        // Reset search if any
        searchInput.value = '';
    });
}

function closeModal() {
    addCourseModal.classList.add('hidden');
    addCourseForm.reset();
}

// Render Courses
function renderCourses(coursesToRender) {
    coursesGrid.innerHTML = '';
    
    courseStats.textContent = `${coursesToRender.length} Course${coursesToRender.length !== 1 ? 's' : ''}`;

    if (coursesToRender.length === 0) {
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    coursesToRender.forEach(course => {
        const card = document.createElement('div');
        card.className = 'course-card';
        
        card.innerHTML = `
            <div class="course-header">
                <span class="course-code">${course.code}</span>
            </div>
            <h3 class="course-title">${course.title}</h3>
            
            <div class="course-details">
                <div class="detail-item">
                    <i class="fa-solid fa-building-columns"></i>
                    <span>${course.department}</span>
                </div>
                <div class="detail-item">
                    <i class="fa-solid fa-calendar-days"></i>
                    <span>Semester ${course.semester}</span>
                </div>
                <div class="detail-item">
                    <i class="fa-solid fa-star"></i>
                    <span>${course.credits} Credits</span>
                </div>
            </div>
            
            <div class="card-actions">
                <button class="action-btn btn-download" onclick="downloadCourseDoc('${course.id}')">
                    <i class="fa-solid fa-download"></i> Download Doc
                </button>
            </div>
        `;
        
        coursesGrid.appendChild(card);
    });
}

// Download functionality
window.downloadCourseDoc = function(courseId) {
    const course = courses.find(c => c.id === courseId);
    if (!course) return;

    // Generate a beautiful text document containing the course info
    const docContent = `
======================================================
                  COURSE DOCUMENT
======================================================

Course Code: ${course.code}
Course Title: ${course.title}
Department: ${course.department}
Semester: ${course.semester}
Credits: ${course.credits}
Program: ${course.program}
Faculty: ${course.faculty}

------------------------------------------------------
This document was dynamically generated by CourseHub.
======================================================
`;

    // Create a Blob from the content
    const blob = new Blob([docContent], { type: 'text/plain' });
    
    // Create a download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${course.code}_${course.title.replace(/\s+/g, '_')}_Doc.txt`;
    
    // Trigger download
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Show brief visual feedback on button
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> Downloaded!';
    btn.style.background = 'rgba(16, 185, 129, 0.3)';
    
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
    }, 2000);
};

// Start App
document.addEventListener('DOMContentLoaded', init);
