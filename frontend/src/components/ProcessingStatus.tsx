import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documentsApi';
import { ProcessingStatus as Status } from '../types/document';

interface ProcessingStatusProps {
  documentId: string;
  onCompleted: () => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ documentId, onCompleted }) => {
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['documentStatus', documentId],
    queryFn: () => documentsApi.getDocumentStatus(documentId),
    refetchInterval: (query) => {
      const data = query.state.data;
      // Stop polling when completed or failed
      if (data?.status === Status.Anonymized || data?.status === Status.Error) {
        if (data.status === Status.Anonymized) {
          onCompleted();
        }
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    enabled: !!documentId,
  });

  if (isLoading) {
    return (
      <div className="status-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Ładowanie statusu...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-container">
        <div className="error">
          <p>❌ Błąd podczas pobierania statusu</p>
          <p>{error.message}</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="status-container">
        <div className="error">
          <p>❌ Nie znaleziono dokumentu</p>
        </div>
      </div>
    );
  }

  const getStatusInfo = (currentStatus: Status) => {
    switch (currentStatus) {
      case Status.Uploaded:
        return {
          text: 'Oczekiwanie na przetworzenie',
          icon: '⏳',
          color: '#ffa500'
        };
      case Status.Processing:
        return {
          text: 'Ekstrakcja tekstu...',
          icon: '🔍',
          color: '#007bff'
        };
      case Status.OCRCompleted:
        return {
          text: 'Analiza danych wrażliwych...',
          icon: '🤖',
          color: '#007bff'
        };
      case Status.DataDetected:
        return {
          text: 'Anonimizacja...',
          icon: '🔒',
          color: '#007bff'
        };
      case Status.Anonymized:
        return {
          text: 'Gotowe! ✓',
          icon: '✅',
          color: '#28a745'
        };
      case Status.Error:
        return {
          text: 'Błąd przetwarzania',
          icon: '❌',
          color: '#dc3545'
        };
      default:
        return {
          text: 'Nieznany status',
          icon: '❓',
          color: '#6c757d'
        };
    }
  };

  const statusInfo = getStatusInfo(status.status);
  const isCompleted = status.status === Status.Anonymized;
  const isFailed = status.status === Status.Error;

  return (
    <div className="status-container">
      <div className="status-header">
        <h3>Status przetwarzania</h3>
        <p className="document-id">ID: {status.documentId}</p>
      </div>

      <div className="status-content">
        <div className="status-icon" style={{ color: statusInfo.color }}>
          {statusInfo.icon}
        </div>
        <div className="status-text">
          <h4 style={{ color: statusInfo.color }}>{statusInfo.text}</h4>
          {status.errorMessage && (
            <p className="error-details">{status.errorMessage}</p>
          )}
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ 
              width: `${status.progress}%`,
              backgroundColor: statusInfo.color
            }}
          ></div>
        </div>
        <p className="progress-text">{status.progress}%</p>
      </div>

      {status.detectedDataCount > 0 && (
        <div className="detected-data">
          <p>🔍 Wykryto {status.detectedDataCount} elementów danych wrażliwych</p>
        </div>
      )}

      {!isCompleted && !isFailed && (
        <div className="processing-indicator">
          <div className="pulse"></div>
          <p>Przetwarzanie w toku...</p>
        </div>
      )}

      <style>{`
        .status-container {
          max-width: 500px;
          margin: 0 auto;
          padding: 24px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .status-header {
          text-align: center;
          margin-bottom: 24px;
        }

        .status-header h3 {
          margin: 0 0 8px 0;
          color: #333;
        }

        .document-id {
          font-size: 12px;
          color: #666;
          font-family: monospace;
          margin: 0;
        }

        .status-content {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
        }

        .status-icon {
          font-size: 32px;
        }

        .status-text h4 {
          margin: 0 0 4px 0;
          font-size: 18px;
        }

        .error-details {
          margin: 0;
          font-size: 14px;
          color: #dc3545;
        }

        .progress-section {
          margin-bottom: 16px;
        }

        .progress-bar {
          width: 100%;
          height: 12px;
          background: #f0f0f0;
          border-radius: 6px;
          overflow: hidden;
          margin-bottom: 8px;
        }

        .progress-fill {
          height: 100%;
          transition: width 0.5s ease;
          border-radius: 6px;
        }

        .progress-text {
          text-align: center;
          margin: 0;
          font-weight: bold;
          color: #333;
        }

        .detected-data {
          background: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 16px;
        }

        .detected-data p {
          margin: 0;
          color: #495057;
          font-size: 14px;
        }

        .processing-indicator {
          display: flex;
          align-items: center;
          gap: 12px;
          justify-content: center;
          color: #666;
        }

        .pulse {
          width: 12px;
          height: 12px;
          background: #007bff;
          border-radius: 50%;
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0% {
            transform: scale(0.95);
            opacity: 1;
          }
          70% {
            transform: scale(1);
            opacity: 0.7;
          }
          100% {
            transform: scale(0.95);
            opacity: 1;
          }
        }

        .loading, .error {
          text-align: center;
          padding: 20px;
        }

        .spinner {
          width: 32px;
          height: 32px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #007bff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ProcessingStatus;