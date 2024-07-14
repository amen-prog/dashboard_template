import React from 'react';
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { BellIcon, PlusIcon } from 'lucide-react'
import { NAV_ITEMS } from '@/constants/navItems';
import { ModeToggle } from "@/components/dark-mode/mode-toggle"

const Header: React.FC = () => {
  return (
    <header className="flex justify-between items-center p-4 bg-background border-b">
      <div className="flex items-center">
        <img src="/api/placeholder/200/50" alt="Company Logo" className="mr-3" />
        <nav className="hidden md:flex space-x-4">
          {NAV_ITEMS.map((item) => (
            <Button key={item.href} variant="ghost" asChild>
              <a href={item.href}>{item.label}</a>
            </Button>
          ))}
        </nav>
      </div>
      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="icon">
          <PlusIcon className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon">
          <BellIcon className="h-4 w-4" />
        </Button>
        <ModeToggle />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/api/placeholder/32/32" alt="@shadcn" />
                <AvatarFallback>SC</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">shadcn</p>
                <p className="text-xs leading-none text-muted-foreground">
                  m@example.com
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Header;