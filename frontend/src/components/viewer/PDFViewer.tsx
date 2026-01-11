import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  analysisId: string;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ analysisId }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);

  const pdfUrl = `${process.env.REACT_APP_API_URL}/uploads/${analysisId}.pdf`;

  return (
    <div className="flex flex-col h-full">
      {/* PDF Controls */}
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center justify-between">
        <button
          onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
          disabled={pageNumber <= 1}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded disabled:opacity-50"
        >
          ←
        </button>
        <span className="text-sm">
          Page {pageNumber} of {numPages}
        </span>
        <button
          onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
          disabled={pageNumber >= numPages}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded disabled:opacity-50"
        >
          →
        </button>
      </div>

      {/* PDF Display */}
      <div className="flex-1 overflow-auto p-4 flex justify-center">
        <Document
          file={pdfUrl}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          loading={<div className="text-center py-8">Loading PDF...</div>}
          error={<div className="text-center py-8 text-red-600">Failed to load PDF</div>}
        >
          <Page
            pageNumber={pageNumber}
            renderTextLayer={true}
            renderAnnotationLayer={true}
            className="shadow-lg"
          />
        </Document>
      </div>
    </div>
  );
};

export default PDFViewer;