import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface Step1Props {
  onSubmit: (data: FormData) => void;
}

const Step1LoadImagery: React.FC = () => {
  const [operatorName, setOperatorName] = useState('');
  const [siteName, setSiteName] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [folderOption, setFolderOption] = useState<string>('1');
  const [customFolderPath, setCustomFolderPath] = useState<string>('');
  const [isFormValid, setIsFormValid] = useState(false);

  useEffect(() => {
    // Check if all required fields are filled
    const isValid = 
      operatorName.trim() !== '' &&
      siteName.trim() !== '' &&
      imageFile !== null &&
      (folderOption !== '3' || (folderOption === '3' && customFolderPath.trim() !== ''));
    
    setIsFormValid(isValid);
  }, [operatorName, siteName, imageFile, folderOption, customFolderPath]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid) return;
  
    const formData = new FormData();
    formData.append('operatorName', operatorName);
    formData.append('siteName', siteName);
    if (imageFile) {
      formData.append('imageFile', imageFile);
    }
    formData.append('folderOption', folderOption);
    if (folderOption === '3') {
      formData.append('customFolderPath', customFolderPath);
    }
  
    try {
      const response = await axios.post('http://localhost:5000/initialize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(response.data);
      // Handle successful submission here (e.g., show a success message, clear form, etc.)
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle error here (e.g., show error message to user)
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Label htmlFor="operatorName">Enter Operator Name</Label>
        <Input 
          id="operatorName" 
          name="operatorName" 
          value={operatorName}
          onChange={(e) => setOperatorName(e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="siteName">Enter Name of Site</Label>
        <Input 
          id="siteName" 
          name="siteName" 
          value={siteName}
          onChange={(e) => setSiteName(e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="imageUpload">Upload Image</Label>
        <Input 
          id="imageUpload" 
          type="file" 
          onChange={(e) => setImageFile(e.target.files ? e.target.files[0] : null)}
        />
      </div>
      <RadioGroup onValueChange={setFolderOption} value={folderOption}>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="1" id="stay_folder" />
          <Label htmlFor="stay_folder">Stay at Current Folder</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="2" id="proj_folder" />
          <Label htmlFor="proj_folder">Create New Folder with Project Name</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="3" id="change_folder" />
          <Label htmlFor="change_folder">Change to Another Folder</Label>
        </div>
      </RadioGroup>
      {folderOption === '3' && (
        <div>
          <Label htmlFor="customFolderPath">Enter Custom Folder Path</Label>
          <Input 
            id="customFolderPath" 
            type="text" 
            placeholder="e.g., C:\Users\YourName\Documents\ProjectFolder"
            value={customFolderPath}
            onChange={(e) => setCustomFolderPath(e.target.value)}
          />
        </div>
      )}
      <Button type="submit" disabled={!isFormValid}>Submit</Button>
    </form>
  );
};

export default Step1LoadImagery;