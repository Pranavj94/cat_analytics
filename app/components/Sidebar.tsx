'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FaDatabase, FaMapMarkerAlt, FaChartBar } from 'react-icons/fa';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar"

const items = [
    {
        title: 'Dummy',
        url: '/reporting',
        icon: FaChartBar
      },
  {
    title: 'Reporting',
    url: '/reporting',
    icon: FaChartBar
  },
  {
    title: 'Data',
    url: '/data',
    icon: FaDatabase
  },
  {
    title: 'Data Quality',
    url: '/dataquality',
    icon: FaMapMarkerAlt
  }
];

export default function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar className="w-1/6 h-full bg-white border-r border-gray-200">
      <SidebarContent className="space-y-8"> {/* Added space between sections */}
        <SidebarGroup>
          <SidebarGroupContent className="space-y-4"> {/* Added space between items */}
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title} className="py-2"> {/* Added vertical padding */}
                  <SidebarMenuButton asChild>
                    <Link 
                      href={item.url}
                      className={`
                        flex items-center gap-3 px-4 py-3 
                        transition-colors rounded-md
                        ${pathname === item.url 
                          ? 'bg-custom-yellow text-gray-700 font-bold' 
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-700'
                        }
                      `}
                    >
                      <item.icon className="text-lg" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}