import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { BellIcon, PlusIcon } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ModeToggle } from "@/components/dark-mode/mode-toggle";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "@/components/dark-mode/theme-provider";

// Import your logo images
import logoLight from "/Logo-light.svg";
import logoDark from "/Logo-dark.svg";
import logoLightShort from "/Logo-light-short.svg";
import logoDarkShort from "/Logo-dark-short.svg";


const NAV_ITEMS = [
  { href: '/', label: 'Dashboard' },
  // { href: '/alarms', label: 'Alarms' },
  // { href: '/assets', label: 'Assets' },
];

const Header: React.FC = () => {
  const location = useLocation();
  const { theme } = useTheme();

  const getLogoSrc = () => {
    if (theme === 'dark') {
      return { full: logoDark, short: logoDarkShort };
    }
    return { full: logoLight, short: logoLightShort };
  };

  const logos = getLogoSrc();
  const navigate = useNavigate();

  return (
    <header className="flex justify-between items-center p-4 bg-background border-b">
      <div className="flex items-center">
        <picture className="mr-3">
          <source media="(min-width: 768px)" srcSet={logos.full} />
          <img src={logos.short} alt="Company Logo" className="h-4 md:h-4" />
        </picture>
        <nav className="hidden md:flex space-x-4">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={`relative py-2 transition-colors delay-75 hover:text-primary ${
                location.pathname === item.href ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              {item.label}
              <span className={`absolute bottom-0 left-0 w-full h-0.5 bg-primary transform origin-left transition-transform duration-200 ease-out ${
                location.pathname === item.href ? 'scale-x-100' : 'scale-x-0'
              } group-hover:scale-x-100`}></span>
            </Link>
          ))}
        </nav>
      </div>
      <div className="flex items-center space-x-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="bg-primary text-primary-foreground hover:bg-primary-foreground hover:text-primary transition-all duration-300 ease-in-out"
          onClick={() => navigate('/new-site')}
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          New Site
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