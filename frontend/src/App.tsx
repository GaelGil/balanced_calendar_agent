import { Route, Routes } from "react-router-dom";
import PrivateRoute from "./components/PrivateRoute";
import Footer from "./components/Layout/Footer";
import Navigation from "./components/Layout/NavBar";
import Home from "./pages/Home";
import AuthPage from "./pages/Auth";
import ProfilePage from "./pages/Profile";
import { useEffect } from "react";
import { getCurrentUser } from "./api/auth";
import { useUser } from "./context/UserContext";
import CalendarPage from "./pages/Calendar";
function App() {
  const { setUser } = useUser();

  useEffect(() => {
    getCurrentUser().then((user) => {
      if (user) {
        setUser(user);
      }
    });
  }, []);

  return (
    <div>
      <Navigation />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<AuthPage />} />
        <Route element={<PrivateRoute />}>
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/profile/:userId" element={<ProfilePage />} />
        </Route>
      </Routes>

      <Footer />
    </div>
  );
}

export default App;
