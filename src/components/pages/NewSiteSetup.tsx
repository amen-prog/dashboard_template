import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const steps = [
  "Load Site Imagery",
  "Define Site Boundaries",
  "Define Site Equipment",
  "Wind Data",
  "Sensor Placement",
  "Export Configuration"
];

const NewSiteSetup: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [siteData, setSiteData] = useState<{
    siteName: string;
    imageFile: File | null;
    hasGeoreferencedImagery: boolean | null;
  }>({
    siteName: '',
    imageFile: null,
    hasGeoreferencedImagery: null,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSiteData({ ...siteData, [e.target.name]: e.target.value });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSiteData({ ...siteData, imageFile: e.target.files[0] });
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <>
            <h2 className="text-lg font-semibold mb-4">Load Site Imagery and Project Data Storage</h2>
            <div className="space-y-4">
              <div>
                <Label htmlFor="siteName">Enter Name of Site</Label>
                <Input id="siteName" name="siteName" value={siteData.siteName} onChange={handleInputChange} />
              </div>
              <div>
                <Label htmlFor="imageUpload">Upload Image</Label>
                <Input id="imageUpload" type="file" onChange={handleFileUpload} />
              </div>
              <RadioGroup onValueChange={(value) => setSiteData({ ...siteData, hasGeoreferencedImagery: value === 'yes' })}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="yes" id="georef-yes" />
                  <Label htmlFor="georef-yes">I have georeferenced site imagery</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="no" id="georef-no" />
                  <Label htmlFor="georef-no">I need help getting georeferenced imagery</Label>
                </div>
              </RadioGroup>
            </div>
          </>
        );
      // Add cases for other steps
      default:
        return <div>Step not implemented yet</div>;
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">New Site Setup</h1>
      <div className="mb-6">
        <ol className="flex items-center w-full text-sm font-medium text-center text-gray-500 dark:text-gray-400 sm:text-base">
          {steps.map((step, index) => (
            <li key={index} className={`flex md:w-full items-center ${index <= currentStep ? 'text-blue-600 dark:text-blue-500' : ''} sm:after:content-[''] after:w-full after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700`}>
              <span className="flex items-center after:content-['/'] sm:after:hidden after:mx-2 after:text-gray-200 dark:after:text-gray-500">
                {index < currentStep ? (
                  <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-2.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"/>
                  </svg>
                ) : (
                  <span className="mr-2">{index + 1}</span>
                )}
                {step}
              </span>
            </li>
          ))}
        </ol>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep]}</CardTitle>
        </CardHeader>
        <CardContent>
          {renderStep()}
        </CardContent>
      </Card>
      <div className="mt-6 flex justify-between">
        <Button onClick={() => setCurrentStep(Math.max(0, currentStep - 1))} disabled={currentStep === 0}>
          Previous
        </Button>
        <Button onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))} disabled={currentStep === steps.length - 1}>
          Next
        </Button>
      </div>
    </div>
  );
};

export default NewSiteSetup;