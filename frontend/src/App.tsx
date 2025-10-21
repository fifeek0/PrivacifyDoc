import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DocumentUpload from './components/DocumentUpload';
import ProcessingStatus from './components/ProcessingStatus';
import DownloadLink from './components/DownloadLink';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5000,
    },
  },
});

type AppState = 'upload' | 'processing' | 'completed';

function App() {
  const [appState, setAppState] = useState<AppState>('upload');
  const [documentId, setDocumentId] = useState<string>('');
  const [originalFileName, setOriginalFileName] = useState<string>('');
  const [detectedDataCount, setDetectedDataCount] = useState<number>(0);

  const handleUploadSuccess = (id: string) => {
    setDocumentId(id);
    setAppState('processing');
  };

  const handleProcessingCompleted = () => {
    setAppState('completed');
  };

  const handleStartOver = () => {
    setAppState('upload');
    setDocumentId('');
    setOriginalFileName('');
    setDetectedDataCount(0);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <header className="app-header">
          <h1>🔒 PrivacifyDoc</h1>
          <p>Automatyczna anonimizacja danych wrażliwych w dokumentach</p>
        </header>

        <main className="app-main">
          {appState === 'upload' && (
            <div className="step">
              <h2>Krok 1: Prześlij dokument</h2>
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            </div>
          )}

          {appState === 'processing' && documentId && (
            <div className="step">
              <h2>Krok 2: Przetwarzanie dokumentu</h2>
              <ProcessingStatus 
                documentId={documentId} 
                onCompleted={handleProcessingCompleted}
              />
            </div>
          )}

          {appState === 'completed' && documentId && (
            <div className="step">
              <h2>Krok 3: Pobierz zanonimizowany dokument</h2>
              <DownloadLink 
                documentId={documentId}
                originalFileName={originalFileName || 'document'}
                detectedDataCount={detectedDataCount}
              />
              <div className="start-over">
                <button onClick={handleStartOver} className="start-over-btn">
                  🔄 Zanonimizuj kolejny dokument
                </button>
              </div>
            </div>
          )}
        </main>

        <footer className="app-footer">
          <p>PrivacifyDoc - Ochrona prywatności w dokumentach</p>
          <p>Obsługiwane typy danych: PESEL, NIP, REGON, Email, Telefon, Imiona, Adresy</p>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;
