import { useState } from 'react';

const PDFInput = () => {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
    };

    const handleUpload = () => {
        const formData = new FormData();
        formData.append('file', selectedFile);

        fetch('http://localhost:3001/upload', {
            method: 'POST',
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                console.log('Success:', data);
                // Handle the response from the server as needed
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    };

    return (
        <div>
            <label htmlFor="pdfInput" className='text-slate-700'>Choose a PDF file:</label>
            <input
                type="file"
                id="pdfInput"
                accept=".pdf"
                onChange={handleFileChange}
            />
            <button onClick={handleUpload} className='bg-blue-400 rounded-md px-4 py-2 text-white'>Upload</button>
        </div>
    );
};

export default PDFInput;
