import { useCallback, useState } from "react";
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export const handleFindMapping = async (uploadedData,setMapping) => {
    try {
        // Ensure uploadedData is an array
        const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
        
        const response = await axios.post(`${API_BASE_URL}/columnmapper/`, dataToSend, {
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

export const handleApplyMapping = async (data, mapping, setUploadedData,setMapping) => {
    try {
        // Transform data by renaming columns according to mapping
        const transformedData = data.map(row => {
            const newRow = {};
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

export const FindConstMapping = async (uploadedData,setConstMapping) => {
  try {
      // Ensure uploadedData is an array
      const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
      
      const response = await axios.post(`${API_BASE_URL}/constructionmapper/`, dataToSend, {
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

export const ApplyConstMapping = async (
    data, 
    constructionMapping,
    setUploadedData
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

export const FindOccMapping = async (uploadedData,setOccMapping) => {
  try {
      // Ensure uploadedData is an array
      const dataToSend = Array.isArray(uploadedData) ? uploadedData : [uploadedData];
      
      const response = await axios.post(`${API_BASE_URL}/occupancymapper/`, dataToSend, {
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

export const ApplyOccMapping = async (
    data, 
    OccupancyMapping,
    setUploadedData
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

export const RunGeocoder = async (data,setUploadedData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/geocoder/`, data, {
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

export const RunCleaner = async (data,setUploadedData) => {
  try {

    
    const response = await axios.post(`${API_BASE_URL}/cleaner/`, data, {
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

export const exportCSV = (data) => {
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