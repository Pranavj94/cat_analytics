'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import  * as api from '@/app/routes/api';
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
      <div className="rounded-md border overflow-x-auto overflow-y-auto">
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

  return (
    <div className="p-6">
      <div className="border border-gray-200 rounded-lg p-4 mb-2 bg-gray-50"> {/* Reduced margin-bottom */}
        <Breadcrumb className="mt-0"> {/* Reduced margin-top */}
          <BreadcrumbList className="flex items-center gap-6">
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => setActiveTab('import')}
                className={`
                  px-3 py-2 rounded-md transition-all duration-200 cursor-pointer
                  flex items-center gap-2
                  ${activeTab === 'import' 
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
                    ? 'text-black font-medium bg-custom-yellow' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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
          <Button onClick={() => api.handleFindMapping(uploadedData,setMapping)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors mr-4">
            Find Mapping
          </Button> 
          <Button onClick={() => api.handleApplyMapping(uploadedData, mapping,setUploadedData,setMapping)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors mr-4">
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      ) : activeTab === 'construction' ? (
        <div className="mb-6">
          <Button onClick={() => api.FindConstMapping(uploadedData,setConstMapping)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors mr-4">
            Find Mapping
          </Button>
          <Button onClick={() => api.ApplyConstMapping(uploadedData, constMapping,setUploadedData)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors">
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      ) : activeTab === 'occupancy' ? (
        <div className="mb-6">
          <Button onClick={() => api.FindOccMapping(uploadedData,setOccMapping)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors mr-4">
            Find Mapping
          </Button>
          <Button onClick={() => api.ApplyOccMapping(uploadedData, occMapping,setUploadedData)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors">
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      ) : activeTab === 'cleaner' ? (
        <div className="mb-6">
          <Button onClick={() => api.RunGeocoder(uploadedData,setUploadedData)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors mr-4">
            Run Geocoder
          </Button>
          <Button onClick={() => api.RunCleaner(uploadedData,setUploadedData)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors">
            Run Data Cleaner
          </Button>
        </div>
      ) : activeTab === 'export' ? (
        <div className="mb-6">
          <Button onClick={() => api.exportCSV(uploadedData)} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-950 transition-colors">
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