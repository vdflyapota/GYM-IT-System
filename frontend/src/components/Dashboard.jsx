import React, { useState, useEffect } from "react";
import "./Dashboard.css";

const Dashboard = () => {
  const [notifications, setNotifications] = useState([]);

  // Fetch notifications from backend every 5 seconds
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8004/notifications");
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        setNotifications(data); // assuming backend returns an array of notifications
      } catch (err) {
        console.error("Error fetching notifications:", err);
      }
    };

    fetchNotifications(); // initial fetch
    const interval = setInterval(fetchNotifications, 5000); // repeat every 5 sec

    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  return (
    <div className="dashboard-container">
      <h1>Activity Dashboard</h1>

      <div className="notifications-panel">
        <h2>Latest Alerts</h2>
        {notifications.length === 0 ? (
          <p>No new notifications.</p>
        ) : (
          <ul>
            {notifications.map((note, index) => (
              <li key={index}>{note.message}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
