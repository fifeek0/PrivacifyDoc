import React, { useState, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { documentsApi } from '../api/documentsApi';

interface DocumentUploadProps {
  onUploadSuccess: (documentId: string) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useMutation({
    mutationFn: documentsApi.uploadDocument,
    onSuccess: (data) => {
      setUploadProgress(0);
      onUploadSuccess(data.documentId);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
      setUploadProgress(0);
    },
  });

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'image/png',
      'image/jpeg',
      'image/jpg'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('Nieobsługiwany format pliku. Dozwolone: PDF, DOCX, TXT, PNG, JPG');
      return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('Plik jest za duży. Maksymalny rozmiar: 10MB');
      return;
    }

    uploadMutation.mutate(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-container">
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''} ${uploadMutation.isPending ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileInput}
          accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
        />
        
        {uploadMutation.isPending ? (
          <div className="upload-progress">
            <div className="spinner"></div>
            <p>Przesyłanie pliku...</p>
            {uploadProgress > 0 && (
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}
          </div>
        ) : (
          <div className="upload-content">
            <div className="upload-icon">📄</div>
            <h3>Przeciągnij plik tutaj lub kliknij, aby wybrać</h3>
            <p>Obsługiwane formaty: PDF, DOCX, TXT, PNG, JPG</p>
            <p>Maksymalny rozmiar: 10MB</p>
          </div>
        )}
      </div>

      {uploadMutation.isError && (
        <div className="error-message">
          <p>❌ Błąd podczas przesyłania pliku</p>
          <p>{uploadMutation.error?.message || 'Nieznany błąd'}</p>
        </div>
      )}

      <style>{`
        .upload-container {
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
        }

        .upload-zone {
          border: 2px dashed #ccc;
          border-radius: 8px;
          padding: 40px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: #fafafa;
        }

        .upload-zone:hover {
          border-color: #007bff;
          background: #f0f8ff;
        }

        .upload-zone.drag-active {
          border-color: #007bff;
          background: #e6f3ff;
        }

        .upload-zone.uploading {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .upload-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .upload-content h3 {
          margin: 0 0 8px 0;
          color: #333;
        }

        .upload-content p {
          margin: 4px 0;
          color: #666;
          font-size: 14px;
        }

        .upload-progress {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #007bff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .progress-bar {
          width: 200px;
          height: 8px;
          background: #f0f0f0;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #007bff;
          transition: width 0.3s ease;
        }

        .error-message {
          margin-top: 16px;
          padding: 12px;
          background: #ffe6e6;
          border: 1px solid #ffcccc;
          border-radius: 4px;
          color: #cc0000;
        }

        .error-message p {
          margin: 4px 0;
        }
      `}</style>
    </div>
  );
};

export default DocumentUpload;