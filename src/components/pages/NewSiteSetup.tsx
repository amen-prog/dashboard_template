// NewSiteSetup.tsx
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Step1Map from '../NewSiteSetup/Step1Map';
import Step2DefineBoundaries from '../NewSiteSetup/Step2DefineBoundaries';
import Step3DefineEquipment from '../NewSiteSetup/Step3DefineEquipment';
import Step4WindData from '../NewSiteSetup/Step4WindData';
import Step5SensorPlacement from '../NewSiteSetup/Step5SensorPlacement';
import Step6ExportConfiguration from '../NewSiteSetup/Step6ExportConfiguration';
import useSiteSetup from '../NewSiteSetup/useSiteSetup';
import StepIndicator from '../NewSiteSetup/StepIndicator';

const steps = [
  { title: "Wind Data", component: Step4WindData },
];

const NewSiteSetup: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  

  const CurrentStepComponent = steps[currentStep].component;

  const handleNext = () => {
    setCurrentStep((prev) => Math.min(steps.length - 1, prev + 1));
  };

  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(0, prev - 1));
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>New Site Setup</CardTitle>
        </CardHeader>
        <CardContent>
          <CurrentStepComponent  />
        </CardContent>
      </Card>
      {/* <div className="mt-6 flex justify-between">
        <Button onClick={handlePrevious} disabled={currentStep === 0}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={currentStep === steps.length - 1}>
          Next
        </Button>
      </div> */}
    </div>
  );
};

export default NewSiteSetup;