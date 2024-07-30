import React, { useState, forwardRef, useCallback  } from 'react';
import axios from 'axios';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ChevronDown,
  ChevronUp,
  Layers,
  Search,
  Pencil,
  Trash2,
  Check,
  MapPin,
} from "lucide-react";

interface EquipmentType {
  id: string;
  name: string;
  sourceHeight: number;
  isEmissionSource: boolean;
}

interface ControlsDropdownProps {
  mapStyles: { name: string; url: string }[];
  changeMapStyle: (url: string) => void;
  searchEnabled: boolean;
  drawingEnabled: boolean;
  equipmentDrawingEnabled: boolean;
  lat: string;
  lng: string;
  setLat: (lat: string) => void;
  setLng: (lng: string) => void;
  searchLocation: () => void;
  drawPolygon: () => void;
  deletePolygon: () => void;
  equipmentTypes: EquipmentType[];  
  setSelectedEquipment: (equipment: EquipmentType | null) => void;
  confirmBoundary: () => void;
  confirmEquipment: () => void;
  isBoundaryConfirmed: boolean;
  isEquipmentConfirmed: boolean;
  currentBoundary: boolean;
  drawnEquipmentLength: number;
}

const DropdownMenuTriggerWrapper = forwardRef<
  HTMLButtonElement,
  React.ComponentPropsWithoutRef<typeof DropdownMenuTrigger>
>((props, forwardedRef) => (
  <DropdownMenuTrigger {...props} ref={forwardedRef} />
));

const ControlsDropdown: React.FC<ControlsDropdownProps> = ({
  mapStyles,
  changeMapStyle,
  searchEnabled,
  drawingEnabled,
  equipmentDrawingEnabled,
  lat,
  lng,
  setLat,
  setLng,
  searchLocation,
  drawPolygon,
  deletePolygon,
  equipmentTypes,
  setSelectedEquipment,
  confirmBoundary,
  confirmEquipment,
  isBoundaryConfirmed,
  isEquipmentConfirmed,
  currentBoundary,
  drawnEquipmentLength,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showLatLng, setShowLatLng] = useState(false);
  const [activeButton, setActiveButton] = useState<string | null>(null);
  const [testMessage, setTestMessage] = useState('');

  const testPostRequest = useCallback(async () => {
    try {
      const response = await axios.post('http://localhost:5000/test-post', { message: 'Hello from frontend' });
      setTestMessage(`POST successful: ${response.data.message}`);
    } catch (error) {
      setTestMessage('POST failed: ' + error.message);
    }
  }, []);
  
  const testGetRequest = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:5000/test-get');
      setTestMessage(`GET successful: ${response.data.message}`);
    } catch (error) {
      setTestMessage('GET failed: ' + error.message);
    }
  }, []);

  const handleButtonClick = (action: () => void, buttonName: string) => {
    action();
    setActiveButton(buttonName);
    setTimeout(() => setActiveButton(null), 200);
  };

  return (
    <TooltipProvider>
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <Tooltip>
          <TooltipTrigger asChild>
            <DropdownMenuTriggerWrapper asChild>
              <Button variant="secondary" className="w-8 h-8 p-0 rounded-full">
                {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </DropdownMenuTriggerWrapper>
          </TooltipTrigger>
          <TooltipContent side="right" align="center" sideOffset={5}>
            <p>Map Controls</p>
          </TooltipContent>
        </Tooltip>
        <DropdownMenuContent className="p-1 w-auto min-w-[40px]" align="start" sideOffset={5}>
          <div className="flex flex-col space-y-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button 
                      variant={activeButton === 'mapStyle' ? 'secondary' : 'ghost'}
                      className="w-8 h-8 p-0"
                      onClick={() => handleButtonClick(() => {}, 'mapStyle')}
                    >
                      <Layers className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="p-1" align="start" sideOffset={5}>
                    {mapStyles.map((style) => (
                      <DropdownMenuItem key={style.name} onSelect={() => changeMapStyle(style.url)}>
                        {style.name}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </TooltipTrigger>
              <TooltipContent side="right" align="center" sideOffset={5}>
                <p>Change Map Style</p>
              </TooltipContent>
            </Tooltip>

            {searchEnabled && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={activeButton === 'toggleLatLng' ? 'secondary' : 'ghost'}
                    className="w-8 h-8 p-0"
                    onClick={() => handleButtonClick(() => setShowLatLng(!showLatLng), 'toggleLatLng')}
                  >
                    <MapPin className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>{showLatLng ? 'Hide' : 'Show'} Lat/Lng Input</p>
                </TooltipContent>
              </Tooltip>
            )}

            {showLatLng && (
              <div className="p-1 space-y-1">
                <Input
                  placeholder="Lat"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  className="w-full text-xs h-6"
                />
                <Input
                  placeholder="Long"
                  value={lng}
                  onChange={(e) => setLng(e.target.value)}
                  className="w-full text-xs h-6"
                />
                <Button 
                  variant={activeButton === 'search' ? 'secondary' : 'ghost'}
                  className="w-full h-6 text-xs"
                  onClick={() => handleButtonClick(searchLocation, 'search')}
                >
                  <Search className="w-3 h-3 mr-1" />
                  Search
                </Button>
              </div>
            )}

            {(drawingEnabled || equipmentDrawingEnabled) && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={activeButton === 'drawPolygon' ? 'secondary' : 'ghost'}
                    className="w-8 h-8 p-0"
                    onClick={() => handleButtonClick(drawPolygon, 'drawPolygon')}
                  >
                    <Pencil className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>Draw Polygon</p>
                </TooltipContent>
              </Tooltip>
            )}

            {(drawingEnabled || equipmentDrawingEnabled) && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={activeButton === 'deletePolygon' ? 'secondary' : 'ghost'}
                    className="w-8 h-8 p-0"
                    onClick={() => handleButtonClick(deletePolygon, 'deletePolygon')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>Delete Polygon</p>
                </TooltipContent>
              </Tooltip>
            )}

            {equipmentDrawingEnabled && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        variant={activeButton === 'selectEquipment' ? 'secondary' : 'ghost'}
                        className="w-8 h-8 p-0"
                        onClick={() => handleButtonClick(() => {}, 'selectEquipment')}
                      >
                        <MapPin className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="p-1" align="start" sideOffset={5}>
                      {equipmentTypes.map(eq => (
                        <DropdownMenuItem key={eq.id} onSelect={() => setSelectedEquipment(eq)}>
                          {eq.name}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>Select Equipment</p>
                </TooltipContent>
              </Tooltip>
            )}

            {drawingEnabled && !isBoundaryConfirmed && currentBoundary && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={activeButton === 'confirmBoundary' ? 'secondary' : 'ghost'}
                    className="w-8 h-8 p-0"
                    onClick={() => handleButtonClick(confirmBoundary, 'confirmBoundary')}
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>Confirm Boundary</p>
                </TooltipContent>
              </Tooltip>
            )}

            {equipmentDrawingEnabled && drawnEquipmentLength > 0 && !isEquipmentConfirmed && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant={activeButton === 'confirmEquipment' ? 'secondary' : 'ghost'}
                    className="w-8 h-8 p-0"
                    onClick={() => handleButtonClick(confirmEquipment, 'confirmEquipment')}
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" align="center" sideOffset={5}>
                  <p>Confirm Equipment</p>
                </TooltipContent>
              </Tooltip>
            )}

            {/* Add these buttons to the dropdown menu content */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant={activeButton === 'testPost' ? 'secondary' : 'ghost'}
                  className="w-8 h-8 p-0"
                  onClick={() => handleButtonClick(testPostRequest, 'testPost')}
                >
                  POST
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" align="center" sideOffset={5}>
                <p>Test POST Request</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant={activeButton === 'testGet' ? 'secondary' : 'ghost'}
                  className="w-8 h-8 p-0"
                  onClick={() => handleButtonClick(testGetRequest, 'testGet')}
                >
                  GET
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" align="center" sideOffset={5}>
                <p>Test GET Request</p>
              </TooltipContent>
            </Tooltip>

            {/* Add this to display the test message */}
            {testMessage && (
              <div className="p-1 text-xs">{testMessage}</div>
            )}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </TooltipProvider>
  );
};

export default ControlsDropdown;