export interface Document {
  id: string;
  originalFileName: string;
  contentType: string;
  uploadDate: string;
  status: ProcessingStatus;
  errorMessage?: string;
  originalFilePath: string;
  anonymizedFilePath?: string;
  detectedSensitiveData: SensitiveData[];
}

export const ProcessingStatus = {
  Uploaded: 'Uploaded',
  Processing: 'Processing',
  OCRCompleted: 'OCRCompleted',
  DataDetected: 'DataDetected',
  Anonymized: 'Anonymized',
  Error: 'Error'
} as const;

export type ProcessingStatus = typeof ProcessingStatus[keyof typeof ProcessingStatus];

export interface SensitiveData {
  type: SensitiveDataType;
  originalValue: string;
  anonymizedValue: string;
  confidence: number;
}

export const SensitiveDataType = {
  PersonName: 'PersonName',
  Address: 'Address',
  PhoneNumber: 'PhoneNumber',
  Email: 'Email',
  PESEL: 'PESEL',
  NIP: 'NIP',
  REGON: 'REGON',
  IDNumber: 'IDNumber',
  PassportNumber: 'PassportNumber',
  BankAccount: 'BankAccount',
  CreditCard: 'CreditCard',
  MedicalData: 'MedicalData',
  Custom: 'Custom'
} as const;

export type SensitiveDataType = typeof SensitiveDataType[keyof typeof SensitiveDataType];

export interface DocumentStatusResponse {
  documentId: string;
  status: ProcessingStatus;
  progress: number;
  detectedDataCount: number;
  errorMessage?: string;
}

export interface UploadResponse {
  documentId: string;
}