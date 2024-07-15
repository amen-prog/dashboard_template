import React from 'react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface Step1Props {
  siteData: {
    siteName: string;
    imageFile: File | null;
    hasGeoreferencedImagery: boolean | null;
  };
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRadioChange: (value: string) => void;
}

const Step1LoadImagery: React.FC<Step1Props> = ({ siteData, onInputChange, onFileUpload, onRadioChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <Label htmlFor="siteName">Enter Name of Site</Label>
        <Input id="siteName" name="siteName" value={siteData.siteName} onChange={onInputChange} />
      </div>
      <div>
        <Label htmlFor="imageUpload">Upload Image</Label>
        <Input id="imageUpload" type="file" onChange={onFileUpload} />
      </div>
      <RadioGroup onValueChange={onRadioChange}>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="yes" id="georef-yes" />
          <Label htmlFor="georef-yes">I have georeferenced site imagery</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="no" id="georef-no" />
          <Label htmlFor="georef-no">I need help getting georeferenced imagery</Label>
        </div>
      </RadioGroup>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline">What is georeferenced imagery?</Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Georeferenced imagery is spatial data that has been aligned to a known coordinate system.</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
};

export default Step1LoadImagery;