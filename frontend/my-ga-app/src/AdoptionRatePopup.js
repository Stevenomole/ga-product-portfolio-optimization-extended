import React, { useState, useEffect } from 'react';

const AdoptionRatePopup = ({ adoptionRate, setAdoptionRate, closeWindow }) => {
    const [localAdoptionRate, setLocalAdoptionRate] = useState(adoptionRate);

    useEffect(() => {
        setLocalAdoptionRate(adoptionRate);
    }, [adoptionRate]);

    const handleInputChange = (index, value) => {
        const newAdoptionRate = [...localAdoptionRate];
        newAdoptionRate[index] = parseFloat(value);
        setLocalAdoptionRate(newAdoptionRate);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setAdoptionRate(localAdoptionRate);
        closeWindow(true);  // Indicate that changes were made
    };

    const popupStyle = {
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: '20px',
        width: '80%',
        maxWidth: '600px', // Reduced max-width for better centering
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    };

    const headerStyle = {
        textAlign: 'center',
        marginBottom: '20px',
        paddingBottom: '10px',
        borderBottom: '1px solid #e0e0e0',
        width: '100%',
    };

    const formStyle = {
        width: '100%',
        maxWidth: '400px', // Adjust this value to control the form width
    };

    const inputGroupStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '15px',
    };

    const labelStyle = {
        marginRight: '10px',
    };

    const inputStyle = {
        padding: '8px',
        border: '1px solid #ccc',
        borderRadius: '4px',
        width: '120px', // Fixed width for all inputs
    };

    const buttonGroupStyle = {
        display: 'flex',
        justifyContent: 'center',
        marginTop: '20px',
    };

    const buttonStyle = {
        padding: '10px 20px',
        backgroundColor: '#4CAF50',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
    };

    return (
        <div style={popupStyle}>
            <div style={headerStyle}>
                <h2>Set Adoption Rates</h2>
            </div>
            <form onSubmit={handleSubmit} style={formStyle}>
                {localAdoptionRate.map((rate, index) => (
                    <div key={index} style={inputGroupStyle}>
                        <label style={labelStyle} htmlFor={`product-${index}`}>Product {index + 1}:</label>
                        <input
                            id={`product-${index}`}
                            type="number"
                            value={rate}
                            onChange={(e) => handleInputChange(index, e.target.value)}
                            step="0.01"
                            min="0"
                            max="1"
                            style={inputStyle}
                        />
                    </div>
                ))}
                <div style={buttonGroupStyle}>
                    <button type="submit" style={buttonStyle} onClick={handleSubmit}>Submit</button>
                </div>
            </form>
        </div>
    );
};

export default AdoptionRatePopup;