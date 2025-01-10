'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

export default function Data() {
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('import');
  const [uploadedData, setUploadedData] = useState(null);
  const [mapping, setMapping] = useState({});

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
        
        setUploadedData(response.data);
        localStorage.setItem('uploadedData', JSON.stringify(response.data));
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error finding mapping:', error.response?.data || error.message);
        } else {
            console.error('Error finding mapping:', error);
        }
    }
};

  return (
    <div>
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
      </div>
      {activeTab === 'import' && (
        <div>
          <div {...getRootProps()} style={{ border: '2px dashed #cccccc', padding: '20px', textAlign: 'center' }}>
            <input {...getInputProps()} />
            {isUploading ? <p>Uploading...</p> : <p>Drag & drop a file here, or click to select one</p>}
          </div>
          {uploadedData && (
            <div style={{ marginTop: '20px' }}>
              <h2>Uploaded Data:</h2>
              {renderTable(uploadedData)}
            </div>
          )}
        </div>
      )}
      {activeTab === 'mapper' && (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ marginBottom: '20px' }}>
            <button className="p-2 bg-blue-500 text-white rounded" onClick={handleFindMapping}>Find Mapping</button>
          </div>
          {uploadedData && (
            <div style={{ marginTop: '20px' }}>
              <h2>Uploaded Data:</h2>
              {renderTable(uploadedData)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}