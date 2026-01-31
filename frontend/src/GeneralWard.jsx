import { useState, useRef } from 'react';
import './index.css';
import './GeneralWard.css';

const API_URL = 'http://localhost:8000';

function GeneralWard({ onBack }) {
    const [image1, setImage1] = useState(null);
    const [image2, setImage2] = useState(null);
    const [image1Preview, setImage1Preview] = useState(null);
    const [image2Preview, setImage2Preview] = useState(null);
    const [isComparing, setIsComparing] = useState(false);
    const [comparisonResult, setComparisonResult] = useState(null);
    const [error, setError] = useState(null);
    const image1InputRef = useRef(null);
    const image2InputRef = useRef(null);

    const handleImage1Select = (event) => {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setImage1(file);
            setImage1Preview(URL.createObjectURL(file));
            setError(null);
        } else {
            alert('Please select a valid image file');
        }
    };

    const handleImage2Select = (event) => {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setImage2(file);
            setImage2Preview(URL.createObjectURL(file));
            setError(null);
        } else {
            alert('Please select a valid image file');
        }
    };

    const handleCompare = async () => {
        if (!image1 || !image2) {
            alert('Please upload both images before comparing');
            return;
        }

        setIsComparing(true);
        setError(null);
        setComparisonResult(null);

        try {
            const formData = new FormData();
            formData.append('image1', image1);
            formData.append('image2', image2);

            console.log('Sending request to:', `${API_URL}/api/compare-ward-images`);
            
            const response = await fetch(`${API_URL}/api/compare-ward-images`, {
                method: 'POST',
                body: formData,
            });

            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log('Result:', result);

            if (!result.success) {
                throw new Error(result.error || 'Comparison failed');
            }

            setComparisonResult(result.comparison_result);
        } catch (err) {
            console.error('Comparison error:', err);
            setError(err.message || 'Failed to connect to server. Please check if backend is running.');
        } finally {
            setIsComparing(false);
        }
    };

    const clearAll = () => {
        setImage1(null);
        setImage2(null);
        setImage1Preview(null);
        setImage2Preview(null);
        setComparisonResult(null);
        setError(null);
    };

    return (
        <div className="general-ward-container">
            <div className="ward-header">
                <button className="btn btn-secondary" onClick={onBack}>
                    ← Back to Dashboard
                </button>
                <h1 className="ward-title">General Ward - Patient Presence Detection</h1>
                <p className="ward-subtitle">Upload two ward images to detect missing patients using AI</p>
            </div>

            <div className="ward-content">
                {/* Image Upload Section */}
                <div className="ward-images-grid">
                    {/* Image 1 */}
                    <div className="ward-image-card">
                        <h3 className="image-card-title">📸 Before Image (Reference)</h3>
                        <div
                            className="image-upload-area"
                            onClick={() => image1InputRef.current?.click()}
                        >
                            {image1Preview ? (
                                <img src={image1Preview} alt="Before" className="uploaded-image" />
                            ) : (
                                <div className="upload-placeholder">
                                    <span className="upload-icon">🖼️</span>
                                    <p>Click to upload reference image</p>
                                    <span className="upload-hint">Ward with all patients present</span>
                                </div>
                            )}
                        </div>
                        <input
                            ref={image1InputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImage1Select}
                            style={{ display: 'none' }}
                        />
                        {image1 && (
                            <p className="image-filename">✓ {image1.name}</p>
                        )}
                    </div>

                    {/* Image 2 */}
                    <div className="ward-image-card">
                        <h3 className="image-card-title">📸 After Image (Current)</h3>
                        <div
                            className="image-upload-area"
                            onClick={() => image2InputRef.current?.click()}
                        >
                            {image2Preview ? (
                                <img src={image2Preview} alt="After" className="uploaded-image" />
                            ) : (
                                <div className="upload-placeholder">
                                    <span className="upload-icon">🖼️</span>
                                    <p>Click to upload current image</p>
                                    <span className="upload-hint">Current ward state to check</span>
                                </div>
                            )}
                        </div>
                        <input
                            ref={image2InputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImage2Select}
                            style={{ display: 'none' }}
                        />
                        {image2 && (
                            <p className="image-filename">✓ {image2.name}</p>
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="ward-actions">
                    <button
                        className="btn btn-primary btn-large"
                        onClick={handleCompare}
                        disabled={!image1 || !image2 || isComparing}
                    >
                        {isComparing ? (
                            <>
                                <span className="loading"></span>
                                Analysing the Ward...
                            </>
                        ) : (
                            <>
                                🤖 Analysing the Ward
                            </>
                        )}
                    </button>
                    {(image1 || image2) && (
                        <button className="btn btn-secondary" onClick={clearAll}>
                            🗑️ Clear All
                        </button>
                    )}
                </div>

                {/* Error Display */}
                {error && (
                    <div className="error-message">
                        <span className="error-icon">⚠️</span>
                        <div>
                            <strong>Error:</strong> {error}
                            {error.includes('GEMINI_API_KEY') && (
                                <p className="error-hint">
                                    Please set your Gemini API key as an environment variable.
                                    Get your key from: <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
                                </p>
                            )}
                        </div>
                    </div>
                )}

                {/* Results Display */}
                {comparisonResult && (
                    <div className="comparison-results">
                        <h2 className="results-title">🔍 Analysis Results</h2>

                        {/* Summary */}
                        <div className="result-summary-card">
                            <div className="summary-header">
                                <span className="summary-icon">📊</span>
                                <h3>Summary</h3>
                            </div>
                            <p className="summary-text">{comparisonResult.summary}</p>
                            {comparisonResult.total_missing > 0 && (
                                <div className="missing-count">
                                    <span className="count-badge">{comparisonResult.total_missing}</span>
                                    <span>Patient(s) Missing</span>
                                </div>
                            )}
                        </div>

                        {/* Missing Patients */}
                        {comparisonResult.missing_patients && comparisonResult.missing_patients.length > 0 && (
                            <div className="missing-patients-section">
                                <h3 className="section-heading">🚨 Missing Patients Detected</h3>
                                <div className="missing-patients-grid">
                                    {comparisonResult.missing_patients.map((patient, index) => (
                                        <div key={index} className="missing-patient-card">
                                            <div className="patient-card-header">
                                                <span className="bed-icon">🛏️</span>
                                                <h4>{patient.bed_number}</h4>
                                            </div>
                                            <p className="patient-description">{patient.description}</p>
                                            <div className="alert-badge-danger">
                                                <span>⚠️ Immediate Attention Required</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* No Changes */}
                        {comparisonResult.total_missing === 0 && (
                            <div className="no-changes-card">
                                <span className="success-icon">✅</span>
                                <h3>All Patients Present</h3>
                                <p>No missing patients detected. All beds are occupied as expected.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default GeneralWard;
