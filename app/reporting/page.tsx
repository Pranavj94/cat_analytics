'use client';

import React from 'react';
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, Controller } from "react-hook-form";
import { z } from "zod";
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from "@/components/ui/label";
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
      reportType: 'Excel',
      edm: '',
      allPortfolios: true,
      portfolios: '',
      allAnalysis: true,
      analysis: '',
    },
  });

  function onSubmit(values: FormData) {
    console.log(values);
  }

  return (
    <div className="flex justify-center items-center min-h-screen p-4">
      <div className="w-full max-w-4xl">
        <h1 className="text-2xl font-bold mb-5">Generate Report</h1>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 border p-4 rounded-lg shadow-lg">
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
                        id="allPortfolios"
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
            <Button type="submit">Submit</Button>
          </form>
        </Form>
      </div>
    </div>
  );
}
