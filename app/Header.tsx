import React from 'react';
import Image from 'next/image';
import mainIcon from './mainicon.jpg';

export default function Header() {
  return (
    <header className="flex items-center p-4 bg-white border-b border-gray-300">
      <Image src={mainIcon} alt="Icon" width={80} height={50} className="h-8 w-8 mr-4" />
      <h1 className="text-xl font-bold text-black"> Analytics</h1>
    </header>
  );
}