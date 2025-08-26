import { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
import { PROJECT_LOGO } from "../../data/ProjectLogo";
import { useUser } from "../../context/UserContext";
import { logout } from "../../api/auth";
const Navigation = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>();
  const [isOpen, setIsOpen] = useState(false);
  const { user, setUser } = useUser();

  const handleLogout = async () => {
    localStorage.removeItem("token");
    try {
      setLoading(true);
      await logout();
      setUser(null);
    } catch (error) {
      alert(`error logging out: ${error}`);
    } finally {
      setLoading(false);
    }
    console.log(loading);
    navigate("/login");
  };

  return (
    <nav className="shadow-sm py-1 ">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 text-decoration-none">
          <img
            src={PROJECT_LOGO}
            alt="Logo"
            className="w-24 h-12 object-contain"
          />
          <span className="font-bold text-xl text-primary-600 no-underline">
            {PROJECT_NAME}
          </span>
        </Link>

        {/* Mobile menu toggle */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-black focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
        >
          <svg
            className="h-6 w-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {isOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 8h16M4 16h16"
              />
            )}
          </svg>
        </button>

        {/* Desktop nav */}
        <div className="hidden md:flex md:items-center space-x-6 font-semibold text-lg">
          {!user ? (
            <Link className="text-decoration-none" to="/login">
              <span className="text-primary-600">Calendar</span>
            </Link>
          ) : (
            <Link className="text-decoration-none" to="/calendar">
              <span className="text-primary-600">Calendar</span>
            </Link>
          )}

          {!user ? (
            <Link className="text-decoration-none" to="/login">
              <span className="text-primary-600">Log In</span>
            </Link>
          ) : (
            <Link
              className="text-decoration-none"
              onClick={handleLogout}
              to="/"
            >
              <span className="text-primary-600">Log Out</span>
            </Link>
          )}
        </div>
      </div>

      {/* Mobile nav */}
      {isOpen && (
        <div className="md:hidden px-4 pb-4 space-y-2 font-semibold text-lg">
          <Link to="/orders" onClick={() => setIsOpen(false)}>
            Orders
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
