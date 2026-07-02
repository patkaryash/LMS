import React from 'react';

const Footer = () => {
  return (
    <footer className="py-4 px-6 text-center text-sm border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1e1e1e] text-gray-600 dark:text-gray-400">
      <p>&copy; {new Date().getFullYear()} Yashwantrao Bhonsale Institute of Technology. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
