'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import EditableMappingTable from "@/app/components/EditableMappingTable";



export default function Data() {
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('import');
  const [uploadedData, setUploadedData] = useState<any[]>([]);
  const [mapping, setMapping] = useState({});
  const [constMapping, setConstMapping] = useState<Record<string, string>>({});

  useEffect(() => {
    localStorage.clear();
    // Load data from local storage when the component mounts
    const storedData = localStorage.getItem('uploadedData');
    if (storedData) {
      setUploadedData(JSON.parse(storedData));
    }
  }, []);

  // Add display section for mapping state
  const renderMappingState = () => {
    return (
      <div className="bg-gray-100 p-4 mb-4 rounded">
        <h3 className="font-bold mb-2">Current Mapping State:</h3>
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(mapping, null, 2)}
        </pre>
      </div>
    );
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      setIsUploading(true);
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/uploadfile/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 5000,
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
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header} className="py-2 px-4 border-b border-gray-300">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {headers.map((header) => (
                <td key={header} className="py-2 px-4 border-b border-gray-300">{row[header]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const handleFindMapping = async () => {
    try {
        // Ensure uploadedData is an array
        const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
        
        const response = await axios.post('http://localhost:8000/columnmapper/', dataToSend, {
            headers: { 'Content-Type': 'application/json' },
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
        const transformedData = data.map(row => {
            const newRow: Record<string, any> = {};
            Object.entries(row).forEach(([key, value]) => {
                const newKey = mapping[key] || key;
                newRow[newKey] = value;
            });
            return newRow;
        });

        // Update state and localStorage
        setUploadedData(transformedData);
        setMapping(mapping);
        localStorage.setItem('uploadedData', JSON.stringify(transformedData));

    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error applying mapping:', error.response?.data || error.message);
        } else {
            console.error('Error applying mapping:', error);
        }
        throw error; // Re-throw to handle in calling code
    }
};

const FindConstMapping = async () => {
  try {
      // Ensure uploadedData is an array
      const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
      
      const response = await axios.post('http://localhost:8000/constructionmapper/', dataToSend, {
          headers: { 'Content-Type': 'application/json' },
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
                BLDGCLASS: constructionMapping[row.BLDGCLASS] || row.BLDGCLASS
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

  return (
    <div className="p-6">
      <div className="flex border-b border-gray-300 mb-4">
        <button
          className={`p-2 ${activeTab === 'import' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('import')}
        >
          Import
        </button>
        <button
          className={`p-2 ${activeTab === 'mapper' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('mapper')}
        >
          Mapper
        </button>
        <button
          className={`p-2 ${activeTab === 'construction' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('construction')}
        >
          Construction
        </button>
        <button
          className={`p-2 ${activeTab === 'occupancy' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('occupancy')}
        >
          Occupancy
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'import' ? (
        <div>
          <div {...getRootProps()} className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input {...getInputProps()} />
            {isUploading ? (
              <p>Uploading...</p>
            ) : (
              <p>Drag & drop a file here, or click to select one</p>
            )}
          </div>
          {uploadedData && (
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-4">Uploaded Data:</h2>
              {renderTable(uploadedData)}
            </div>
          )}
        </div>
      ) : activeTab === 'mapper' ? (
        <div>
          <Button 
            onClick={handleFindMapping}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Find Mapping
          </Button>
          <Button 
            onClick={() => handleApplyMapping(uploadedData, mapping)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      ) : activeTab === 'construction' ? (
        <div>
          <Button
            onClick={FindConstMapping}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Find Mapping
          </Button>
          <Button 
            onClick={() => ApplyConstMapping(uploadedData, constMapping)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Apply Mappings
          </Button>
          {Object.keys(constMapping).length > 0 && (
            <EditableMappingTable mapping={constMapping} setMapping={setConstMapping} />
          )}
        </div>
      ) : (
        // Occupancy tab
        <div>
          <Button 
            onClick={handleFindMapping}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Find Mapping
          </Button>
          <Button 
            onClick={() => handleApplyMapping(uploadedData, mapping)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors mb-4"
          >
            Apply Mappings
          </Button>
          {Object.keys(mapping).length > 0 && (
            <EditableMappingTable mapping={mapping} setMapping={setMapping} />
          )}
        </div>
      )}
    </div>
  );
}