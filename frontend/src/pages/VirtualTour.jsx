import React from 'react';
import './VirtualTour.css';

const VirtualTour = () => {
  return (
    <div className="virtual-tour-container">
      <h1>Virtual Gym Tour</h1>
      <p className="tour-description">
        Explore our state-of-the-art facilities with this 360° interactive tour.
        Click and drag to look around each area.
      </p>
      
      <div className="tour-sections">
        <div className="tour-section">
          <h2>Main Gym Floor</h2>
          <div className="tour-viewer">
            {/* Placeholder for 360 viewer - will use iframe from external service */}
            <div className="viewer-placeholder">
              <p>🔍 360° View Loading...</p>
              <p><em>Integrated with Photo Sphere Viewer or Google Street View API</em></p>
              <div className="demo-controls">
                <button className="tour-btn">← Rotate Left</button>
                <button className="tour-btn">↑ Look Up</button>
                <button className="tour-btn">→ Rotate Right</button>
                <button className="tour-btn">↓ Look Down</button>
              </div>
            </div>
          </div>
          <p className="area-description">
            Our main training area with premium equipment, cardio machines, and free weights.
          </p>
        </div>
        
        <div className="tour-section">
          <h2>Group Classes Studio</h2>
          <div className="tour-viewer">
            <div className="viewer-placeholder">
              <p>🎥 Video Walkthrough Available</p>
              <video controls className="tour-video">
                <source src="/videos/studio-tour.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
        
        <div className="tour-section">
          <h2>Locker Rooms & Amenities</h2>
          <div className="image-gallery">
            <div className="gallery-image"><span>🚿 Shower Area</span></div>
            <div className="gallery-image"><span>🧺 Locker Area</span></div>
            <div className="gallery-image"><span>💆‍♂️ Sauna</span></div>
          </div>
        </div>
      </div>
      
      <div className="tour-instructions">
        <h3>How to Navigate:</h3>
        <ul>
          <li>↕️ <strong>Desktop:</strong> Click and drag to look around</li>
          <li>📱 <strong>Mobile:</strong> Swipe to rotate view, pinch to zoom</li>
          <li>🎯 <strong>Hotspots:</strong> Click on markers to move between areas</li>
          <li>🔊 <strong>Audio Guide:</strong> Click speaker icon for narration</li>
        </ul>
      </div>
      
      <div className="tour-footer">
        <button className="primary-btn">Start Full Tour</button>
        <button className="secondary-btn">Download Floor Plan (PDF)</button>
        <button className="secondary-btn">Book a Real Tour</button>
      </div>
    </div>
  );
};

export default VirtualTour;