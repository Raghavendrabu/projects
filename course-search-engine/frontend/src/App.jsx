// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import CourseDetail from './pages/CourseDetail';
import Admin from './pages/Admin';
import { Link } from 'react-router-dom';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="navbar">
          <div className="navbar-brand">
            <Link to="/"><h1>Course Search Engine</h1></Link>
          </div>
          <nav className="nav-links">
            <Link to="/admin" className="nav-link">Admin / Add Course</Link>
          </nav>
        </header>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/course/:id" element={<CourseDetail />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; {new Date().getFullYear()} University CSE. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
