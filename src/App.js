import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Navbar from "./Components/Navbar";
import Hero from "./Components/Hero";
import Intro from "./Components/Intro";
import Featuredphotos from "./Components/Featuredphotos";
import Gallery from "./Components/Gallery";
import Login from "./Components/Login";
import ClubInfo from "./Components/ClubInfo";
import Footer from "./Components/Footer";
import Contests from "./Components/contests";


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("token");
      setIsAuthenticated(!!token);
    };

    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/home" element={<><Hero /><Intro /><Featuredphotos /></>} />
        <Route path="/gallery" element={<Gallery isAuthenticated={isAuthenticated} />} />
        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/club_info" element={<ClubInfo />} />
        <Route path="/contests" element={<Contests />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;