import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import PopupContent from './PopupContent';
import AdoptionRatePopup from './AdoptionRatePopup';
import backgroundImage from './images/background.jpeg';

const modules = [
  'Module 1', 'Module 2', 'Module 3', 'Module 4',
  'Module 5', 'Module 6', 'Module 7', 'Module 8',
  'Module 9', 'Module 10', 'Module 11', 'Module 12'
];

function App() {
    const [params, setParams] = useState({
        population: 100,
        generations: 50,
        mutationRate: 0.1,
        crossoverRate: 0.5,
    });
    const [defaultInteractionValue, setDefaultInteractionValue] = useState(20);
    const [defaultInteractions, setDefaultInteractions] = useState(
        Object.fromEntries(modules.map(module => [module, 20]))
    );
    const [customInteractions, setCustomInteractions] = useState({});
    const [informationFlow, setInformationFlow] = useState(
        Object.fromEntries(modules.map(module => [module, 0]))
    );
    const [customInformationFlow, setCustomInformationFlow] = useState({});
    const [result, setResult] = useState(null);
    const [dependencies, setDependencies] = useState({});
    const [error, setError] = useState(null);
    const [popupValues, setPopupValues] = useState({});
    const [defaultInformationFlowValue, setDefaultInformationFlowValue] = useState(0);
    const [adoptionRate, setAdoptionRate] = useState(Array(9).fill(0));
    const [customChanges, setCustomChanges] = useState({
        interaction: {},
        information: {}
    });
    const [adoptionRateChanged, setAdoptionRateChanged] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        fetch('/get-preprocessed-data')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.dependencies) {
                    setDependencies(data.dependencies);
                } else {
                    setError("No dependencies data in the response");
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        if (Object.keys(dependencies).length > 0) {
            const initialPopupValues = {};
            modules.forEach(module => {
                const moduleNumber = parseInt(module.split(' ')[1], 10);
                const moduleDependencies = dependencies[moduleNumber] || [];
                
                // Set interaction popup values
                initialPopupValues[`interaction-${module}`] = {};
                moduleDependencies.forEach(depNumber => {
                    const depModule = `Module ${depNumber}`;
                    initialPopupValues[`interaction-${module}`][`${depModule}-${module}`] = defaultInteractions[module];
                });

                // Set information flow popup values
                initialPopupValues[`information-${module}`] = {};
                moduleDependencies.forEach(depNumber => {
                    const depModule = `Module ${depNumber}`;
                    initialPopupValues[`information-${module}`][`${depModule}-${module}`] = informationFlow[module];
                });
            });

            setPopupValues(initialPopupValues);
        }
    }, [dependencies, defaultInteractions, informationFlow]);

    const updatePopupValues = (type, module, value) => {
        setPopupValues(prev => {
            const key = `${type}-${module}`;
            const currentValues = prev[key] || {};
            const updatedValues = {...currentValues};
            
            // Get the dependencies for this module
            const moduleDependencies = dependencies[parseInt(module.split(' ')[1], 10)] || [];
            
            // Update all popup values for this module
            moduleDependencies.forEach(depNumber => {
                const depModule = `Module ${depNumber}`;
                updatedValues[`${depModule}-${module}`] = value;
            });
            
            return {...prev, [key]: updatedValues};
        });
    };

    const checkAndUpdateDefaultValue = (newValues, type) => {
        const uniqueValues = new Set(Object.values(newValues));
        if (uniqueValues.size === 1) {
            const uniformValue = uniqueValues.values().next().value;
            if (type === 'interaction') {
                setDefaultInteractionValue(uniformValue);
            } else if (type === 'information') {
                setDefaultInformationFlowValue(uniformValue);
            }
        }
    };

    const handleDefaultInteractionChange = (module, value) => {
        const newValue = value === '' ? '' : parseFloat(value);
        setDefaultInteractions(prev => {
            const newInteractions = {...prev, [module]: newValue};
            checkAndUpdateDefaultValue(newInteractions, 'interaction');
            return newInteractions;
        });
        updatePopupValues('interaction', module, newValue);
    };

    const handleInformationFlowChange = (module, value) => {
        const newValue = value === '' ? '' : parseFloat(value);
        setInformationFlow(prev => {
            const newFlow = {...prev, [module]: newValue};
            checkAndUpdateDefaultValue(newFlow, 'information');
            return newFlow;
        });
        updatePopupValues('information', module, newValue);
    };

    const handlePopupSubmit = (module, type, values) => {
        setPopupValues(prev => ({
            ...prev,
            [`${type}-${module}`]: values
        }));

        if (type === 'interaction') {
            setCustomInteractions(prev => ({...prev, ...values}));
        } else {
            setCustomInformationFlow(prev => ({...prev, ...values}));
        }

        // Check if at least one value is different
        const allValues = Object.values(values);
        const uniqueValues = new Set(allValues);
        const isCustom = uniqueValues.size > 1 || (uniqueValues.size === 1 && !uniqueValues.has(''));

        setCustomChanges(prev => ({
            ...prev,
            [type]: {
                ...prev[type],
                [module]: isCustom
            }
        }));

        // Get all popup values for this module
        const allPopupValues = {...popupValues[`${type}-${module}`], ...values};

        // Check if all popup values are the same
        if (uniqueValues.size === 1 && Object.keys(allPopupValues).length === dependencies[parseInt(module.split(' ')[1], 10)].length) {
            const uniformValue = uniqueValues.values().next().value;
            if (type === 'interaction') {
                setDefaultInteractions(prev => ({
                    ...prev,
                    [module]: uniformValue
                }));
            } else {
                setInformationFlow(prev => ({
                    ...prev,
                    [module]: uniformValue
                }));
            }
        }
    };

    const handleDefaultValueChange = (type, value) => {
        const newValue = value === '' ? '' : parseFloat(value);
        
        if (type === 'interaction') {
            setDefaultInteractionValue(newValue);
            setDefaultInteractions(prev => {
                const newInteractions = {...prev};
                modules.forEach(module => {
                    newInteractions[module] = newValue;
                    updatePopupValues('interaction', module, newValue);
                });
                return newInteractions;
            });
        } else {
            setDefaultInformationFlowValue(newValue);
            setInformationFlow(prev => {
                const newFlow = {...prev};
                modules.forEach(module => {
                    newFlow[module] = newValue;
                    updatePopupValues('information', module, newValue);
                });
                return newFlow;
            });
        }
    };

    const openModal = (module, type) => {
        const width = 600;
        const height = 400;
        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;
        const newWindow = window.open('', '', `width=${width},height=${height},left=${left},top=${top}`);
        newWindow.document.write('<div id="popup-root"></div>');
        newWindow.document.close();
        const popupRoot = newWindow.document.getElementById('popup-root');
        
        const closeWindow = () => {
            newWindow.close();
        };

        ReactDOM.createRoot(popupRoot).render(
            <PopupContent
                module={module}
                dependencies={dependencies}
                customInteractions={customInteractions}
                informationFlow={informationFlow}
                defaultInteractions={defaultInteractions}
                popupValues={popupValues[`${type}-${module}`] || {}}
                handlePopupSubmit={(values) => handlePopupSubmit(module, type, values)}
                closeWindow={closeWindow}
                modalType={type}
            />
        );
    };

    const openAdoptionRateModal = () => {
        const width = 400;
        const height = 500;
        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;
        const newWindow = window.open('', '', `width=${width},height=${height},left=${left},top=${top}`);
        newWindow.document.write('<div id="adoption-rate-root"></div>');
        newWindow.document.body.style.margin = '0';
        newWindow.document.body.style.padding = '0';
        newWindow.document.body.style.backgroundColor = '#ffffff';
        newWindow.document.close();
        const popupRoot = newWindow.document.getElementById('adoption-rate-root');
        
        const closeWindow = (isChanged) => {
            setAdoptionRateChanged(isChanged);
            newWindow.close();
        };

        ReactDOM.createRoot(popupRoot).render(
            <AdoptionRatePopup
                adoptionRate={adoptionRate}
                setAdoptionRate={setAdoptionRate}
                closeWindow={closeWindow}
            />
        );
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const interactionMatrix = buildInteractionMatrix(customInteractions);
            const informationMatrix = buildInteractionMatrix(customInformationFlow);
            const headers = {
                'Content-Type': 'application/json',
                // Add any other necessary headers here
            };
            console.log('Request Headers:', headers); // Log headers for inspection

            const data = {
                ...params,
                interactionMatrix,
                informationMatrix,
                adoptionRate
            };

            const response = await fetch('/run-ga', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const responseData = await response.json();
            setResult(responseData);
        } catch (error) {
            setError(`Failed to run optimization: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const buildInteractionMatrix = (interactions) => {
        const matrix = {};
        modules.forEach(module1 => {
            modules.forEach(module2 => {
                if (module1 !== module2) {
                    const key = `${module1}-${module2}`;
                    if (interactions === customInformationFlow) {
                        matrix[key] = interactions[key] || informationFlow[module1] || 0;
                    } else {
                        matrix[key] = interactions[key] || defaultInteractions[module1] || 0;
                    }
                }
            });
        });
        return matrix;
    };

    const handleParamChange = (e) => {
        const { name, value } = e.target;
        setParams(prevParams => ({
            ...prevParams,
            [name]: value
        }));
    };

    const getPopupTriggerStyle = (module, type) => {
        const baseStyle = {
            padding: '5px 10px',
            margin: '5px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            width: '80px',
            height: '40px'
        };

        if (customChanges[type][module]) {
            return {
                ...baseStyle,
                backgroundColor: type === 'interaction' ? '#006400' : '#00008B',
                color: 'white'
            };
        }

        return {
            ...baseStyle,
            backgroundColor: type === 'interaction' ? '#E0FFE0' : '#E6F3FF',
            color: '#333333'
        };
    };

    const getAdoptionRateTriggerStyle = () => {
        const baseStyle = {
            padding: '5px 10px',
            margin: '5px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
        };

        return {
            ...baseStyle,
            backgroundColor: adoptionRateChanged ? '#8B0000' : '#FFCCCB',
            color: adoptionRateChanged ? 'white' : 'black'
        };
    };

    const formatMoney = (amount) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
    };

    const formatResult = (result) => {
        if (!result) return null;

        const totalCost = result.fitness;
        const products = result.product_selection;
        const modules = result.best_solution;

        return (
            <div className="result-container">
                <div className="result-summary">
                    <div className="cost-and-products">
                        <div className="total-cost">
                            <h3>Net Portfolio Profit</h3>
                            <p>{formatMoney(totalCost)}</p>
                        </div>
                        <div className="selected-products">
                        <h3>Optimal Product Portfolio</h3>
                            <ul>
                                {Object.entries(products).map(([family, product]) => {
                                    const productName = Object.keys(product)[0];  // Product name
                                    const [productCost, launchTime] = Object.values(product)[0];  // [Cost, Launch Time]

                                    return (
                                        <li key={family} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span className="product-name">
                                                Family {family}: Product {productName}
                                            </span>
                                            <span className="product-cost">
                                                {formatMoney(productCost)}
                                            </span>
                                            <span className="launch-time">
                                                Launch Time: {launchTime}
                                            </span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    </div>
                    <div className="module-schedule">
                        <h3>Module Schedule</h3>
                        <table className="schedule-table">
                            <thead>
                                <tr>
                                    <th>Module</th>
                                    <th>Start Date</th>
                                    <th>End Date</th>
                                    <th>Duration</th>
                                    <th>Supplier</th>
                                    <th>Module Cost</th>
                                    <th>Crashing</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(modules).map(([module, details]) => (
                                    <tr key={module}>
                                        <td>Module {module}</td>
                                        <td>{details[0]}</td>
                                        <td>{details[3]}</td>
                                        <td>{details[3] - details[0]} weeks</td>
                                        <td>{details[1] > 0 ? details[1] : 'None'}</td>
                                        <td>{`${details[4].toLocaleString('en-US', { style: 'currency', currency: 'USD' })}`}</td>
                                        <td className={details[2] > 0 ? 'crashing' : 'no-crashing'}>
                                            {details[2] > 0 ? `${details[2]} week(s)` : 'No'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="app-container" style={{backgroundImage: `url(${backgroundImage})`}}>
            <header>
                <h1>Product Portfolio Optimizer</h1>
            </header>
            <main>
                <section className="input-section white-background">
                    <h2>Input Parameters</h2>
                    {error && <div className="error-message">Error: {error}</div>}
                    <form onSubmit={handleSubmit}>
                        <div className="params-grid">
                            <div className="param-input">
                                <label htmlFor="population">Population Size:</label>
                                <input
                                    id="population"
                                    type="number"
                                    name="population"
                                    value={params.population}
                                    onChange={handleParamChange}
                                    min="1"
                                />
                            </div>
                            <div className="param-input">
                                <label htmlFor="generations">Number of Generations:</label>
                                <input
                                    id="generations"
                                    type="number"
                                    name="generations"
                                    value={params.generations}
                                    onChange={handleParamChange}
                                    min="1"
                                />
                            </div>
                            <div className="param-input">
                                <label htmlFor="mutationRate">Mutation Rate:</label>
                                <input
                                    id="mutationRate"
                                    type="number"
                                    name="mutationRate"
                                    value={params.mutationRate}
                                    onChange={handleParamChange}
                                    step="0.01"
                                    min="0"
                                    max="1"
                                />
                            </div>
                            <div className="param-input">
                                <label htmlFor="crossoverRate">Crossover Rate:</label>
                                <input
                                    id="crossoverRate"
                                    type="number"
                                    name="crossoverRate"
                                    value={params.crossoverRate}
                                    onChange={handleParamChange}
                                    step="0.01"
                                    min="0"
                                    max="1"
                                />
                            </div>
                        </div>

                        <div className="interaction-flow-header">
                            <h3>Interaction and Information Flow Parameters</h3>
                            <div className="default-values">
                                <div className="default-inputs">
                                    <div className="input-group">
                                        <label htmlFor="defaultInteraction">Default Interaction:</label>
                                        <input
                                            id="defaultInteraction"
                                            type="number"
                                            value={defaultInteractionValue}
                                            onChange={(e) => handleDefaultValueChange('interaction', e.target.value)}
                                            step="1"
                                        />
                                    </div>
                                    <div className="input-group">
                                        <label htmlFor="defaultInfoFlow">Default Information Flow:</label>
                                        <input
                                            id="defaultInfoFlow"
                                            type="number"
                                            value={defaultInformationFlowValue}
                                            onChange={(e) => handleDefaultValueChange('information', e.target.value)}
                                            step="1"
                                        />
                                    </div>
                                </div>
                                <button 
                                    type="button" 
                                    onClick={openAdoptionRateModal} 
                                    style={getAdoptionRateTriggerStyle()}
                                >
                                    Set Adoption Rates
                                </button>
                            </div>
                        </div>

                        <div className="modules-grid">
                            {modules.map(module => (
                                <div key={module} className="module-item">
                                    <h4>{module}</h4>
                                    <div className="input-group">
                                        <div className="input-label-box">
                                            <label>Interaction</label>
                                            <input
                                                type="number"
                                                value={defaultInteractions[module]}
                                                onChange={(e) => handleDefaultInteractionChange(module, e.target.value)}
                                                step="1"
                                            />
                                        </div>
                                        <button 
                                            type="button" 
                                            onClick={() => openModal(module, 'interaction')}
                                            style={getPopupTriggerStyle(module, 'interaction')}
                                        >
                                            <span>Custom</span>
                                            <span>Interaction</span>
                                        </button>
                                    </div>
                                    <div className="input-group">
                                        <div className="input-label-box">
                                            <label>Info Flow</label>
                                            <input
                                                type="number"
                                                value={informationFlow[module]}
                                                onChange={(e) => handleInformationFlowChange(module, e.target.value)}
                                                step="1"
                                            />
                                        </div>
                                        <button 
                                            type="button" 
                                            onClick={() => openModal(module, 'information')}
                                            style={getPopupTriggerStyle(module, 'information')}
                                        >
                                            <span>Custom</span>
                                            <span>Info Flow</span>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="submit-btn-container">
                            <button type="submit" className="submit-btn" onClick={handleSubmit} disabled={isLoading}>
                                {isLoading ? (
                                    <>
                                        <span style={{visibility: 'hidden'}}>Optimize</span>
                                        <div className="loading-spinner"></div>
                                    </>
                                ) : (
                                    'Optimize'
                                )}
                            </button>
                        </div>
                    </form>
                </section>
                
                <section className="results-section">
                    {result && formatResult(result)}
                </section>
            </main>
        </div>
    );
}

export default App;
