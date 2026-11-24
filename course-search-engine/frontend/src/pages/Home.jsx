// frontend/src/pages/Home.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, BookOpen } from 'lucide-react';
import { searchCourses, getAllCourses } from '../api';

function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await getAllCourses();
      setCourses(data);
    } catch (err) {
      setError('Failed to fetch courses. Please make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchCourses();
      return;
    }

    try {
      setLoading(true);
      const data = await searchCourses(searchQuery);
      setCourses(data);
    } catch (err) {
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="search-section">
        <h2>Find Your Next Course</h2>
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search by course code or title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button">Search</button>
          </div>
        </form>
      </div>

      <div className="results-section">
        {loading ? (
          <div className="loading">Loading courses...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : courses.length === 0 ? (
          <div className="no-results">No courses found matching your criteria.</div>
        ) : (
          <div className="courses-grid">
            {courses.map(course => (
              <div key={course._id} className="course-card">
                <div className="course-card-header">
                  <span className="course-code">{course.courseCode}</span>
                  <span className="course-credits">{course.credits} Credits</span>
                </div>
                <h3 className="course-title">{course.courseTitle}</h3>
                <p className="course-aims">{course.aims.substring(0, 100)}...</p>
                <div className="course-card-footer">
                  <Link to={`/course/${course._id}`} className="view-details-btn">
                    <BookOpen size={16} /> View Syllabus
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
