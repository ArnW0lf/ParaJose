import React, { useState } from 'react';
import GeneratorForm from './components/GeneratorForm';
import PublicationCard from './components/PublicationCard';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
    // Estado que almacena el resultado de Gemini
    const [currentAdaptations, setCurrentAdaptations] = useState(null);
    const [masterImageURL, setMasterImageURL] = useState('');

    const handleAdaptationSuccess = (data, imageURL) => {
        // La data contiene post_id y el objeto 'adaptaciones'
        setCurrentAdaptations(data.adaptaciones);
        setMasterImageURL(imageURL);
        console.log("Adaptaciones recibidas:", data);
    };

    const platforms = ['facebook', 'instagram', 'linkedin', 'whatsapp', 'tiktok'];

    return (
        <div className="container py-5">
            <h1 className="text-center fw-bold text-dark mb-4">Portal de Publicación LLM</h1>
            <p className="text-center text-muted mb-5">Backend Django + Gemini, Frontend React</p>
            
            <GeneratorForm onAdaptationSuccess={handleAdaptationSuccess} />

            {/* Sección de Publicación (Solo visible si hay datos) */}
            {currentAdaptations && (
                <div id="publication-area" className="mt-5">
                    <h2 className="mb-4 border-bottom pb-2">2. Revisar y Publicar Borradores</h2>
                    
                    <div className="row g-4">
                        {platforms.map(platform => (
                            <div key={platform} className="col-lg-6 col-md-6 col-sm-12">
                                <PublicationCard 
                                    data={currentAdaptations[platform]} 
                                    platform={platform} 
                                    imageURL={masterImageURL}
                                />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;