import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Database } from 'lucide-react';
import { importCoursesFromCsv } from '../api';

function Admin() {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
        setError(null);
        setSuccess(null);
      } else {
        setError('Please select a valid CSV file.');
        setFile(null);
      }
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }
    
    try {
      setImporting(true);
      setError(null);
      const result = await importCoursesFromCsv(file);
      setSuccess(result.message || 'Courses successfully imported to database!');
      setFile(null);
    } catch (err) {
      setError('Failed to import CSV. Please ensure the file format is correct.');
      console.error(err);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>Bulk import course data directly into MongoDB using CSV files.</p>
      </div>

      {error && <div className="admin-alert error"><AlertCircle size={20} /> {error}</div>}
      {success && <div className="admin-alert success"><CheckCircle size={20} /> {success}</div>}

      <div className="admin-card">
        <div className="card-header">
          <Database size={24} />
          <h2>CSV Data Import</h2>
        </div>
        
        <div className="card-body">
          <div className="format-info">
            <h3>Expected CSV Format:</h3>
            <code>courseCode, courseTitle, credits, ltp, aims, objectives, outcomes, unit1, unit2, unit3, unit4, unit5, assessmentQuiz, assessmentTest, assessmentAssignment, assessmentSEE, textbooks, grading</code>
            <p className="note">Note: Use | (pipe) to separate multiple objectives, outcomes, or textbooks within a single cell.</p>
          </div>

          <div className="upload-box">
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFileChange}
              className="hidden-input"
              id="csv-upload"
            />
            <label htmlFor="csv-upload" className={`file-drop-area ${file ? 'has-file' : ''}`}>
              <FileSpreadsheet size={48} className="upload-icon" />
              <div className="file-info">
                <strong>{file ? file.name : 'Select CSV File'}</strong>
                <span>{file ? 'Click to change file' : 'Browse your computer'}</span>
              </div>
            </label>
            
            <button 
              onClick={handleImport} 
              disabled={!file || importing}
              className="primary-btn import-btn"
            >
              {importing ? (
                <>Importing...</>
              ) : (
                <><Upload size={18} /> Start Bulk Import</>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="admin-card instructions">
        <div className="card-header">
          <h3>Helpful Tips</h3>
        </div>
        <div className="card-body">
          <ul>
            <li><strong>Objectives:</strong> Use <code>1. To...|2. To...</code></li>
            <li><strong>Outcomes:</strong> Use <code>CO1: Description|CO2: Description</code></li>
            <li><strong>Units:</strong> Use <code>UNIT I - TITLE: Topic 1, Topic 2, Topic 3</code></li>
            <li><strong>Grading:</strong> Use <code>91+: O (Outstanding)|81-90: A+ (Excellent)</code></li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Admin;
