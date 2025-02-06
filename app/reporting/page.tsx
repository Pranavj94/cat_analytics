'use client';

import React, { useState, useEffect, FormEvent } from 'react';
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from "@/components/ui/label";
import * as XLSX from 'xlsx';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

type ReportType = 'Excel' | 'PowerBI';

const formSchema = z.object({
  reportName: z.string().min(1, { message: "Report Name is required." }),
  reportType: z.enum(['Excel', 'PowerBI']),
  edm: z.string().min(1, { message: "EDM is required." }),
  allPortfolios: z.boolean(),
  portfolios: z.string().optional(),
  allAnalysis: z.boolean(),
  analysis: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

export default function ReportingPage() {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      reportName: '',
      reportType: 'Excel',
      edm: '',
      allPortfolios: true,
      portfolios: '',
      allAnalysis: true,
      analysis: '',
    },
  });

  const [alert, setAlert] = useState<{ type: 'error' | 'success'; message: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const generateReport = async (e: FormEvent) => {
    e.preventDefault();
    const formData = form.getValues();

    if (!formData.edm.trim()) {
      setAlert({
        type: 'error',
        message: 'EDM is required'
      });
      return;
    }

  setIsLoading(true);
  setAlert(null);

  const endpoint = formData.reportType === 'Excel' 
    ? '/generateExcelReport/' 
    : '/generatePowerBIReport/';

  try {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        reportName: formData.reportName,
        edmValue: formData.edm,
        allPortfolios: formData.allPortfolios,
        portfolios: formData.portfolios,
        allAnalysis: formData.allAnalysis,
        analysis: formData.analysis,
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    if (result.status === 'success') {
      const fileResponse = await fetch(`/backend/rms_utils/${result.file_path}`);
      const blob = await fileResponse.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${formData.reportName}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setAlert({
        type: 'success',
        message: `${formData.reportType} report generated successfully`
      });
    }
  } catch (error) {
      let errorMessage = 'An unexpected error occurred';

      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Unable to connect to the server. Please check your connection.';
        } else if (error.message.includes('HTTP error! status: 422')) {
          errorMessage = 'Invalid data provided. Please check your inputs.';
        } else if (error.message.includes('HTTP error! status: 500')) {
          errorMessage = 'Server error. Please try again later.';
        }
      }

      setAlert({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isClient) {
    return null;
  }

  return (
    <div className="flex justify-center items-center min-h-screen p-4">
      <div className="w-full max-w-4xl">
        <h1 className="text-2xl font-bold mb-5">Generate Report</h1>
        {alert && (
          <Alert variant={alert.type === 'error' ? 'destructive' : 'default'}>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>{alert.type === 'error' ? 'Error' : 'Success'}</AlertTitle>
            <AlertDescription>{alert.message}</AlertDescription>
          </Alert>
        )}
        <Form {...form}>
          <form onSubmit={generateReport} className="space-y-8 border p-4 rounded-lg shadow-lg">
            <FormField
              control={form.control}
              name="reportName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Report Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter Report Name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="reportType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Report Type</FormLabel>
                  <FormControl>
                    <RadioGroup value={field.value} onValueChange={field.onChange}>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="Excel" id="excel" />
                        <Label htmlFor="excel">Excel</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="PowerBI" id="powerbi" />
                        <Label htmlFor="powerbi">PowerBI</Label>
                      </div>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="edm"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>EDM</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter EDM" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="allPortfolios"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                      />
                      <Label htmlFor="allPortfolios" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        All Portfolios
                      </Label>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {!form.watch('allPortfolios') && (
              <FormField
                control={form.control}
                name="portfolios"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Portfolios</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter Portfolios" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            <FormField
              control={form.control}
              name="allAnalysis"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                        id="allAnalysis"
                      />
                      <Label htmlFor="allAnalysis" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        All Analysis
                      </Label>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {!form.watch('allAnalysis') && (
              <FormField
                control={form.control}
                name="analysis"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Analysis</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter Analysis" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            <Button type="submit" disabled={isLoading}>
              Generate Report
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );

}
