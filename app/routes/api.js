import { useCallback, useState } from "react";
import axios from "axios";



export const handleFindMapping = async () => {
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

export const handleApplyMapping = async (data, mapping) => {
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