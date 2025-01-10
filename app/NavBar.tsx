'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FaDatabase, FaMapMarkerAlt, FaChartBar } from 'react-icons/fa';

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col p-4 bg-white border border-gray-300 w-1/6 h-full">
      <Link
        href="/reporting"
        className={`flex items-center mb-4 p-3 transition duration-300 ease-in-out ${
          pathname === '/reporting'
            ? 'bg-blue-200 text-blue-800 border-r-4 border-blue-400'
            : 'text-black hover:bg-blue-100 hover:text-blue-800'
        }`}
      >
        <FaChartBar className="mr-2" />
        Reporting
      </Link>
      <Link
        href="/data"
        className={`flex items-center mb-4 p-3 transition duration-300 ease-in-out ${
          pathname === '/data'
            ? 'bg-blue-200 text-blue-800 border-r-4 border-blue-400'
            : 'text-black hover:bg-blue-100 hover:text-blue-800'
        }`}
      >
        <FaDatabase className="mr-2" />
        Data
      </Link>
      <Link
        href="/dataquality"
        className={`flex items-center mb-4 p-3 transition duration-300 ease-in-out ${
          pathname === '/dataquality'
            ? 'bg-blue-200 text-blue-800 border-r-4 border-blue-400'
            : 'text-black hover:bg-blue-100 hover:text-blue-800'
        }`}
      >
        <FaMapMarkerAlt className="mr-2" />
        Data Quality
      </Link>

    </nav>
  );
}