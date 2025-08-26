// import { Link } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
const Footer = () => {
  return (
    <footer className="py-6 text-center text-secondary-300">
      <div className="max-w-7xl mx-auto px-4">
        <p className="mb-0">© 2025 {PROJECT_NAME}. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
