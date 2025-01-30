'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

import EditableMappingTable from "@/app/components/EditableMappingTable";
import { FiUpload, FiMap, FiHome, FiUsers, FiTool, FiDownload } from "react-icons/fi";

export default function Data() {
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('import');
  const [uploadedData, setUploadedData] = useState<any[]>([]);
  const [mapping, setMapping] = useState({});
  const [constMapping, setConstMapping] = useState<Record<string, string>>({});
  const [occMapping, setOccMapping] = useState<Record<string, string>>({});

  useEffect(() => {
    localStorage.clear();
    // Load data from local storage when the component mounts
    const storedData = localStorage.getItem('uploadedData');
    if (storedData) {
      setUploadedData(JSON.parse(storedData));
    }
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      setIsUploading(true);
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/uploadfile/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000, // 60 seconds timeout
      });

      const data = response.data;
      setUploadedData(data); // Store the uploaded data
      localStorage.setItem('uploadedData', JSON.stringify(data)); // Save data to local storage
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const renderTable = (data: any[]) => {
    if (!data || !Array.isArray(data) || data.length === 0) return null;

    const headers = Object.keys(data[0]);

    return (
      <div className="rounded-md border">
        <Table>
          <TableCaption>SOV</TableCaption>
          <TableHeader>
            <TableRow>
              {headers.map((header) => (
                <TableHead key={header}>{header}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {headers.map((header) => (
                  <TableCell key={`${rowIndex}-${header}`}>{row[header]}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };

  const handleFindMapping = async () => {
    try {
        // Ensure uploadedData is an array
        const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
        
        const response = await axios.post('http://localhost:8000/columnmapper/', dataToSend, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 60000, // 60 seconds timeout
        });
        
        setMapping(response.data.mapping);
    
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error finding mapping:', error.response?.data || error.message);
        } else {
            console.error('Error finding mapping:', error);
        }
    }
};

  const handleApplyMapping = async (data: any[], mapping: Record<string, string>) => {
    try {

        // Transform data by renaming columns according to mapping
        const transformedData = data.map((row, index) => {
            const newRow: Record<string, any> = {};
            Object.entries(row).forEach(([key, value]) => {
                const newKey = mapping[key] || key;
                if (key === 'Occupancy') {
                    console.log(`Processing Occupancy in row ${index}:`, {
                        originalKey: key,
                        mappedKey: mapping[key],
                        value: value
                    });
                }
                newRow[newKey] = value;
            });
            return newRow;
        });



        // Update state and localStorage
        setUploadedData(transformedData);
        setMapping(mapping);
        localStorage.setItem('uploadedData', JSON.stringify(transformedData));

    } catch (error) {
        console.error('Error in handleApplyMapping:', error);
        throw error;
    }
};

const FindConstMapping = async () => {
  try {
      // Ensure uploadedData is an array
      const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
      
      const response = await axios.post('http://localhost:8000/constructionmapper/', dataToSend, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 60000, // 60 seconds timeout
      });
      
      setConstMapping(response.data.mapping);
  
  } catch (error) {
      if (axios.isAxiosError(error)) {
          console.error('Error finding mapping:', error.response?.data || error.message);
      } else {
          console.error('Error finding mapping:', error);
      }
  }
};

const ApplyConstMapping = async (
    data: any[], 
    constructionMapping: Record<string, string>
) => {
    try {
        // Transform BLDNGCLASS values according to construction mapping
        const transformedData = data.map(row => {
            return {
                ...row,
                BLDGCLASS: constructionMapping[row.BLDGCLASS] || row.BLDGCLASS,
                BLDGSCHEME: 'RMS'
            };
        });

        // Update state and localStorage
        setUploadedData(transformedData);
        localStorage.setItem('uploadedData', JSON.stringify(transformedData));
        
        return transformedData;
    } catch (error) {
        console.error('Error applying construction mapping:', error);
        throw error;
    }
};

const FindOccMapping = async () => {
  try {
      // Ensure uploadedData is an array
      const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
      
      const response = await axios.post('http://localhost:8000/occupancymapper/', dataToSend, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 60000, // 60 seconds timeout
      });
      
      setOccMapping(response.data.mapping);
  
  } catch (error) {
      if (axios.isAxiosError(error)) {
          console.error('Error finding mapping:', error.response?.data || error.message);
      } else {
          console.error('Error finding mapping:', error);
      }
  }
};

const ApplyOccMapping = async (
    data: any[], 
    OccupancyMapping: Record<string, string>
) => {
    try {
        // Transform BLDNGCLASS values according to construction mapping
        const transformedData = data.map(row => {
            return {
                ...row,
                OCCTYPE: OccupancyMapping[row.OCCTYPE] || row.OCCTYPE,
                OCCSCHEME: 'ATC'
            };
        });

        // Update state and localStorage
        setUploadedData(transformedData);
        localStorage.setItem('uploadedData', JSON.stringify(transformedData));
        
        return transformedData;
    } catch (error) {
        console.error('Error applying construction mapping:', error);
        throw error;
    }
};

const RunGeocoder = async (data: any[]) => {
  try {
    const response = await axios.post('http://localhost:8000/geocoder/', data, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000,
    });
    
    const geocodedData = response.data.data;

    if (!Array.isArray(geocodedData)) {
      throw new Error('Invalid response format');
    }
    
    // Update state and localStorage
    setUploadedData(geocodedData);
    localStorage.setItem('uploadedData', JSON.stringify(geocodedData));
    
    return geocodedData;
    
  } catch (error) {
    console.error('Error during geocoding:', error);
    throw error;
  }
};

const RunCleaner = async (data: any[]) => {
  try {

    
    const response = await axios.post('http://localhost:8000/cleaner/', data, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000,
    });
    
    const geocodedData = response.data;


    
    // Update state and localStorage
    setUploadedData(geocodedData);
    localStorage.setItem('uploadedData', JSON.stringify(geocodedData));
    

    return geocodedData;
    
  } catch (error) {
    console.error('Error during geocoding:', error);

    throw error;
  }
};

const exportCSV = (data: any[]) => {
  const csvContent = [
    Object.keys(data[0]).join(','), // header row
    ...data.map(row => Object.values(row).join(',')) // data rows
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'exported_data.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

  return (
    <div className="p-6">
      <div className="border border-gray-200 rounded-lg p-4 mb-4 bg-gray-50">
        <Breadcrumb>
          <BreadcrumbList className="flex items-center gap-6">
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('import')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'import' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiUpload className="text-lg" />
                Import
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-400">→</BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('mapper')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'mapper' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiMap className="text-lg" />
                Mapper
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-400">→</BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('construction')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'construction' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiHome className="text-lg" />
                Construction
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-400">→</BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('occupancy')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'occupancy' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiUsers className="text-lg" />
                Occupancy
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-400">→</BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('cleaner')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'cleaner' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiTool className="text-lg" />
                Cleaner
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-400">→</BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('export')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'export' 
                    ? 'text-blue-600 font-medium bg-blue-50' 
                    : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                  }
                `}
              >
                <FiDownload className="text-lg" />
                Export
              </BreadcrumbLink>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </div>
      {/* Tab-specific content */}
      {activeTab === 'import' ? (
        <div {...getRootProps()} className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-6">
          <input {...getInputProps()} />
          {isUploading ? (
            <p>Uploading...</p>
          ) : (
            <p>Drag & drop a file here, or click to select one</p>
          )}
        </div>
      ) : activeTab === 'mapper' ? (
        <div className="mb-6">
          <Button onClick={handleFindMapping} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mr-4">
            Find Mapping
          </Button>
          <Button onClick={() => handleApplyMapping(uploadedData, mapping)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      ) : activeTab === 'construction' ? (
        <div className="mb-6">
          <Button onClick={FindConstMapping} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mr-4">
            Find Mapping
          </Button>
          <Button onClick={() => ApplyConstMapping(uploadedData, constMapping)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            Apply Mappings
          </Button>
          {Object.keys(constMapping).length > 0 && (
            <EditableMappingTable mapping={constMapping} setMapping={setConstMapping} />
          )}
        </div>
      ) : activeTab === 'occupancy' ?(
        <div className="mb-6">
          <Button onClick={FindOccMapping} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mr-4">
            Find Mapping
          </Button>
          <Button onClick={() => ApplyOccMapping(uploadedData, occMapping)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={occMapping} setMapping={setOccMapping} />
          )}
        </div>
      ): activeTab === 'cleaner' ? (
        <div className="mb-6">
          <Button onClick={() => RunGeocoder(uploadedData)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mr-4">
            Run Geocoder
          </Button>
          <Button onClick={() => RunCleaner(uploadedData)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            Run Data Cleaner
          </Button>
        </div>
      ) : activeTab === 'export' ? (
        <div className="mb-6">
          <Button onClick={() => exportCSV(uploadedData)} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
            Export Data
          </Button>
        </div>
      ) : null}

      {/* Show uploaded data table for all tabs */}
      {uploadedData && uploadedData.length > 0 && (
        <div className="mt-6">
          {renderTable(uploadedData)}
        </div>
      )}
    </div>
  );
}