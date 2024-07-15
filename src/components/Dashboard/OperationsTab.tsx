import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

const OperationsTab: React.FC = () => {
  const [date, setDate] = useState<Date | undefined>(new Date());

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div className="grid grid-cols-2 gap-4 w-2/3">
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Methane Emissions</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Add methane emissions data/chart here */}
              <p>Emissions data visualization</p>
            </CardContent>
          </Card>
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Dummy Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Some other relevant information</p>
            </CardContent>
          </Card>
        </div>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[280px] justify-start text-left font-normal",
                !date && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date ? format(date, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0">
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>
      
      <div className="flex space-x-4">
        <div className="w-3/4 bg-secondary h-96">Map Placeholder</div>
        <div className="w-1/4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Map Legend</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Add map legend here */}
              <p>Legend details</p>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <div className="w-full">
        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Add timeline scroller here */}
            <div className="h-16 bg-secondary">
              Timeline placeholder
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OperationsTab;