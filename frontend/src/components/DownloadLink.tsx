import React, { useState } from 'react';
import { documentsApi } from '../api/documentsApi';

interface DownloadLinkProps {
  documentId: string;
  originalFileName: string;
  detectedDataCount: number;
}

const DownloadLink: React.FC<DownloadLinkProps> = ({ 
  documentId, 
  originalFileName, 
  detectedDataCount 
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);

    try {
      const blob = await documentsApi.downloadDocument(documentId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const fileExtension = originalFileName.split('.').pop() || 'txt';
      const baseName = originalFileName.replace(/\.[^/.]+$/, '');
      link.download = `${baseName}_anonymized.${fileExtension}`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Download failed:', error);
      setDownloadError('Nie udało się pobrać pliku. Spróbuj ponownie.');
    } finally {
      setIsDownloading(false);
    }
  };

  const downloadMetadata = () => {
    const metadata = {
      documentId,
      originalFileName,
      detectedDataCount,
      anonymizedAt: new Date().toISOString(),
      note: 'Ten plik zawiera metadane o procesie anonimizacji dokumentu.'
    };

    const blob = new Blob([JSON.stringify(metadata, null, 2)], { 
      type: 'application/json' 
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${documentId}_metadata.json`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="download-container">
      <div className="download-header">
        <h3>✅ Dokument został zanonimizowany!</h3>
        <p>Twój dokument jest gotowy do pobrania</p>
      </div>

      <div className="file-info">
        <div className="info-row">
          <span className="label">Oryginalny plik:</span>
          <span className="value">{originalFileName}</span>
        </div>
        <div className="info-row">
          <span className="label">Wykryte dane wrażliwe:</span>
          <span className="value">{detectedDataCount} elementów</span>
        </div>
        <div className="info-row">
          <span className="label">ID dokumentu:</span>
          <span className="value document-id">{documentId}</span>
        </div>
      </div>

      <div className="download-actions">
        <button 
          className="download-btn primary"
          onClick={handleDownload}
          disabled={isDownloading}
        >
          {isDownloading ? (
            <>
              <div className="spinner"></div>
              Pobieranie...
            </>
          ) : (
            <>
              📥 Pobierz zanonimizowany dokument
            </>
          )}
        </button>

        <button 
          className="download-btn secondary"
          onClick={downloadMetadata}
        >
          📋 Pobierz metadane (JSON)
        </button>
      </div>

      {downloadError && (
        <div className="error-message">
          <p>❌ {downloadError}</p>
        </div>
      )}

      <div className="download-info">
        <h4>ℹ️ Informacje o anonimizacji</h4>
        <ul>
          <li>Wszystkie wykryte dane wrażliwe zostały zastąpione placeholderami</li>
          <li>Oryginalny dokument pozostaje niezmieniony</li>
          <li>Proces anonimizacji jest nieodwracalny</li>
          <li>Sprawdź dokument przed udostępnieniem</li>
        </ul>
      </div>

      <style>{`
        .download-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 24px;
          border: 1px solid #28a745;
          border-radius: 8px;
          background: #f8fff9;
        }

        .download-header {
          text-align: center;
          margin-bottom: 24px;
        }

        .download-header h3 {
          margin: 0 0 8px 0;
          color: #28a745;
          font-size: 24px;
        }

        .download-header p {
          margin: 0;
          color: #666;
        }

        .file-info {
          background: white;
          padding: 16px;
          border-radius: 6px;
          margin-bottom: 24px;
          border: 1px solid #e9ecef;
        }

        .info-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          padding: 4px 0;
        }

        .info-row:last-child {
          margin-bottom: 0;
        }

        .label {
          font-weight: 500;
          color: #495057;
        }

        .value {
          color: #212529;
        }

        .document-id {
          font-family: monospace;
          font-size: 12px;
          background: #f8f9fa;
          padding: 2px 6px;
          border-radius: 3px;
        }

        .download-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 24px;
        }

        .download-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .download-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .download-btn.primary {
          background: #28a745;
          color: white;
        }

        .download-btn.primary:hover:not(:disabled) {
          background: #218838;
        }

        .download-btn.secondary {
          background: #6c757d;
          color: white;
        }

        .download-btn.secondary:hover {
          background: #5a6268;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid transparent;
          border-top: 2px solid currentColor;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-message {
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          color: #721c24;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 16px;
        }

        .error-message p {
          margin: 0;
        }

        .download-info {
          background: #e7f3ff;
          padding: 16px;
          border-radius: 6px;
          border-left: 4px solid #007bff;
        }

        .download-info h4 {
          margin: 0 0 12px 0;
          color: #004085;
          font-size: 16px;
        }

        .download-info ul {
          margin: 0;
          padding-left: 20px;
          color: #004085;
        }

        .download-info li {
          margin-bottom: 4px;
          font-size: 14px;
        }

        .download-info li:last-child {
          margin-bottom: 0;
        }

        @media (min-width: 768px) {
          .download-actions {
            flex-direction: row;
          }
        }
      `}</style>
    </div>
  );
};

export default DownloadLink;