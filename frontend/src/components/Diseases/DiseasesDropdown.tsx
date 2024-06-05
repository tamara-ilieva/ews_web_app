import React, { useEffect, useState } from 'react';
import ImageService from '../../client/services/ImagesService';

const DiseaseDropdown = ({ selectedDisease, onDiseaseChange }) => {
    const [diseases, setDiseases] = useState([]);

    useEffect(() => {
        const fetchDiseases = async () => {
            try {
                const data = await ImageService.getAllDiseases();
                setDiseases(data.data);
            } catch (error) {
                console.error('Failed to fetch diseases:', error);
            }
        };

        fetchDiseases();
    }, []);

    return (
        <select value={selectedDisease} onChange={(e) => onDiseaseChange(e.target.value)}>
            <option value="">Select Disease</option>
            {diseases.map((disease) => (
                <option key={disease.id} value={disease.id}>
                    {disease.name}
                </option>
            ))}
        </select>
    );
};

export default DiseaseDropdown;
