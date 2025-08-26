import { Link } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
import { PROJECT_LOGO } from "../../data/ProjectLogo";
import { useUser } from "../../context/UserContext";

const HomeBanner = () => {
  const { user } = useUser();

  return (
    <>
      <div className="min-h-[80vh] flex items-center justify-center bg-gradient-to-r from-[#e3f0ff] to-[#f8fafd] text-primary-600">
        <div className="max-w-7xl mx-auto px-4 w-full">
          <div className="flex flex-col-reverse md:flex-row items-center">
            {/* Left content */}
            <div className="w-full md:w-1/2 text-left">
              <h1 className="font-extrabold  text-4xl md:text-5xl mb-6 ">
                {PROJECT_NAME}
              </h1>
              <p className="text-lg md:text-xl text-gray-700 mb-8 text-secondary-300">
                Your personal calendar assistant to help you balance your work
                life. Our agent can assist you in creating events to balance
                your work live.
              </p>

              {!user ? (
                <Link to="/login">
                  <button className="px-10 py-4 text-lg font-bold rounded-lg bg-[#1976d2] text-white border-none shadow-md hover:shadow-lg transition">
                    View Content
                  </button>
                </Link>
              ) : (
                <Link to="/calendar">
                  <button className="px-10 py-4 text-lg font-bold rounded-lg bg-[#1976d2] text-white border-none shadow-md hover:shadow-lg transition">
                    View Content
                  </button>
                </Link>
              )}
            </div>

            {/* Right image */}
            <div className="w-full md:w-1/2 text-center mb-10 md:mb-0">
              <img
                src={PROJECT_LOGO}
                alt="Order Agent"
                className="w-80 max-w-[90%] mx-auto rounded-3xl shadow-[0_4px_24px_rgba(25,118,210,0.10)]"
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default HomeBanner;
