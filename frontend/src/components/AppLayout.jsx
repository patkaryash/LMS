import React from 'react';
import Sidebar from './Sidebar.jsx';
import HeaderBar from './HeaderBar.jsx';
import Footer from './Footer.tsx';
import { useColorMode } from '../contexts/ThemeContext';

const AppLayout = ({ children }) => {
  const { mode } = useColorMode();

  // Sync Tailwind's dark mode class with ThemeContext
  React.useEffect(() => {
    const root = document.documentElement;
    if (mode === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
  }, [mode]);

  return (
    <div className={`min-h-screen flex flex-col ${mode === 'dark' ? 'bg-[#1e1e1e] text-gray-100' : 'bg-gray-50 text-gray-900'}`}>
      {/* Fixed header with logo + college name + top nav */}
      <HeaderBar />

      {/* Sidebar under the header */}
      <Sidebar />

      {/* Main content on the right, shifts when sidebar expands */}
      <main className="flex-1 transition-all duration-300 ease-out ml-16 peer-hover:ml-64 pt-14">
        <div className="p-4 sm:p-6 md:p-8">
          {children}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AppLayout;
