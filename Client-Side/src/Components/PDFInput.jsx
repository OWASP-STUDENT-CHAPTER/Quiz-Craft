import { useState } from 'react'

const PDFInput = () => {
    const [selectedFile, setSelectedFile] = useState(null)

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
    }

    return (
        <form>
            <label htmlFor="pdfInput">Choose a PDF file:</label>
            <input
                type="file"
                id="pdfInput"
                accept=".pdf"
                onChange={handleFileChange}
            />
        </form>
    )
}

export default PDFInput