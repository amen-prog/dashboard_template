// useSiteSetup.ts
import { useState } from 'react';

export interface SiteData {
  siteName: string;
  imageFile: File | null;
  hasGeoreferencedImagery: boolean | null;
  // Add other properties as needed
}

const useSiteSetup = () => {
  const [siteData, setSiteData] = useState<SiteData>({
    siteName: '',
    imageFile: null,
    hasGeoreferencedImagery: null,
  });

  const updateSiteData = (newData: Partial<SiteData>) => {
    setSiteData((prevData) => ({ ...prevData, ...newData }));
  };

  return { siteData, updateSiteData };
};

export default useSiteSetup;