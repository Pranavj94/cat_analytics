'use client';

import React, { useState, FormEvent } from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { Alert, AlertTitle, AlertDescription } from '../../components/ui/alert';

type ReportType = 'Excel' | 'PowerBI';

interface FormData {
  reportType: ReportType;
  edm: string;
  aal: boolean;
}

interface AlertState {
  type: 'success' | 'error';
  message: string;
}

const ReportGeneration = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [alert, setAlert] = useState<AlertState | null>(null);
  const [formData, setFormData] = useState<FormData>({
    reportType: 'PowerBI',
    edm: '',
    aal: false
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const generateReport = async (e: FormEvent) => {
    e.preventDefault();
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
          edmValue: formData.edm,
          aal: formData.aal
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setAlert({
        type: 'success',
        message: `${formData.reportType} report generated successfully`
      });
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

  return (
    <div className="flex min-h-screen bg-gray-50">
      <main className="flex-1 p-8 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900">Report Generation</h1>
        
        {alert && (
          <Alert className={`mt-4 ${alert.type === 'error' ? 'bg-red-50' : 'bg-green-50'}`}>
            {alert.type === 'error' ? (
              <AlertCircle className="h-4 w-4 text-red-600" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            )}
            <AlertTitle className={alert.type === 'error' ? 'text-red-800' : 'text-green-800'}>
              {alert.type === 'error' ? 'Error' : 'Success'}
            </AlertTitle>
            <AlertDescription className={alert.type === 'error' ? 'text-red-700' : 'text-green-700'}>
              {alert.message}
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={generateReport} className="mt-6 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900">Report Type</h3>
            <div className="flex gap-4 mt-2">
              <label className={`cursor-pointer p-3 border rounded-lg transition-colors ${
                formData.reportType === 'Excel' 
                  ? 'bg-blue-500 text-white border-blue-600' 
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}>
                <input
                  type="radio"
                  name="reportType"
                  value="Excel"
                  checked={formData.reportType === 'Excel'}
                  onChange={handleInputChange}
                  className="hidden"
                />
                Excel
              </label>
              <label className={`cursor-pointer p-3 border rounded-lg transition-colors ${
                formData.reportType === 'PowerBI'
                  ? 'bg-blue-500 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}>
                <input
                  type="radio"
                  name="reportType"
                  value="PowerBI"
                  checked={formData.reportType === 'PowerBI'}
                  onChange={handleInputChange}
                  className="hidden"
                />
                PowerBI
              </label>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">EDM</label>
              <input
                type="text"
                name="edm"
                value={formData.edm}
                onChange={handleInputChange}
                className="mt-1 w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter EDM value"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                name="aal"
                checked={formData.aal}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                id="aal"
              />
              <label htmlFor="aal" className="text-sm font-medium text-gray-700">
                AAL
              </label>
            </div>
          </div>

          <button 
            type="submit"
            disabled={isLoading}
            className={`w-full px-4 py-2 text-white rounded-lg shadow-sm transition-colors ${
              isLoading
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            {isLoading ? 'Generating Report...' : 'Generate Report'}
          </button>
        </form>
      </main>
    </div>
  );
};

export default ReportGeneration;