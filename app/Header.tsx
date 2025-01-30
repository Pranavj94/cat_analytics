import React from 'react';
import Image from 'next/image';
import mainIcon from './mainicon.jpg';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function Header() {
  return (
    <header className="flex justify-between items-center p-4 bg-white border-b border-gray-300">
      <div className="flex items-center">
        <Image src={mainIcon} alt="Icon" width={80} height={50} className="h-8 w-8 mr-4" />
        <h1 className="text-xl font-bold text-black">CAT APP</h1>
      </div>
      <Avatar className="hover:opacity-80 cursor-pointer mr-4">
        <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
    </header>
  );
}