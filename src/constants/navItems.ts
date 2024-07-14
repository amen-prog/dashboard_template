interface NavItem {
    href: string;
    label: string;
  }
  
  export const NAV_ITEMS: NavItem[] = [
    { href: '/', label: 'Dashboard' },
    { href: '/alarms', label: 'Alarms' },
    { href: '/assets', label: 'Assets' },
  ];