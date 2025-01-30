import React from 'react';
import Image from 'next/image';
import mainIcon from './mainicon.jpg';
import ardonagh from './ardonagh1.jpg';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function Header() {
  return (
    <header className="flex justify-between items-center p-2 bg-custom-green border-b border-gray-300">
      <div className="flex items-center">
        <Image src={ardonagh} alt="Icon" width={45} height={50} className="mr-4" />
      </div>
      <Avatar className="hover:opacity-80 cursor-pointer mr-4">
        <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
    </header>
  );
}