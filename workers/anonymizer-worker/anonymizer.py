import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PatternBasedAnonymizer:
    """
    Pattern-based anonymizer using regex patterns for Polish sensitive data detection.
    This is a baseline implementation before AI integration.
    """
    
    def __init__(self):
        self.patterns = {
            'PESEL': {
                'pattern': r'\b\d{11}\b',
                'confidence': 0.95,
                'description': 'Polish Personal Identification Number'
            },
            'NIP': {
                'pattern': r'\b\d{10}\b',
                'confidence': 0.95,
                'description': 'Polish Tax Identification Number'
            },
            'REGON': {
                'pattern': r'\b\d{9}(\d{5})?\b',
                'confidence': 0.95,
                'description': 'Polish Business Registry Number'
            },
            'EMAIL': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'confidence': 0.90,
                'description': 'Email address'
            },
            'PHONE': {
                'pattern': r'(\+48)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}',
                'confidence': 0.85,
                'description': 'Polish phone number'
            },
            'POSTAL_CODE': {
                'pattern': r'\b\d{2}-\d{3}\b',
                'confidence': 0.90,
                'description': 'Polish postal code'
            },
            'PERSON_NAME': {
                'pattern': r'\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\b',
                'confidence': 0.75,
                'description': 'Polish person name (heuristic)'
            },
            'ADDRESS': {
                'pattern': r'\b(ul\.|al\.|pl\.|os\.)\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+\d+[a-zA-Z]?\b',
                'confidence': 0.80,
                'description': 'Polish street address'
            }
        }
    
    def detect_sensitive_data(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect sensitive data in text using regex patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detection dictionaries with keys: type, value, start, end, confidence
        """
        detections = []
        
        for data_type, pattern_info in self.patterns.items():
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']
            
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Additional validation for specific types
                    if self._validate_detection(data_type, match.group()):
                        detection = {
                            'type': data_type,
                            'value': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': confidence
                        }
                        detections.append(detection)
                        logger.debug(f"Detected {data_type}: {match.group()} at position {match.start()}-{match.end()}")
            
            except Exception as e:
                logger.error(f"Error processing pattern {data_type}: {e}")
        
        # Remove duplicates and overlapping detections
        detections = self._remove_overlapping_detections(detections)
        
        logger.info(f"Detected {len(detections)} sensitive data items")
        return detections
    
    def _validate_detection(self, data_type: str, value: str) -> bool:
        """
        Additional validation for specific data types to reduce false positives.
        """
        if data_type == 'PESEL':
            # Basic PESEL validation (11 digits, basic checksum)
            if len(value) != 11 or not value.isdigit():
                return False
            # Simple checksum validation
            weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
            checksum = sum(int(value[i]) * weights[i] for i in range(10)) % 10
            return (10 - checksum) % 10 == int(value[10])
        
        elif data_type == 'NIP':
            # Basic NIP validation (10 digits)
            return len(value) == 10 and value.isdigit()
        
        elif data_type == 'REGON':
            # Basic REGON validation (9 or 14 digits)
            return value.isdigit() and len(value) in [9, 14]
        
        elif data_type == 'EMAIL':
            # Additional email validation
            return '@' in value and '.' in value.split('@')[1]
        
        elif data_type == 'PERSON_NAME':
            # Filter out common false positives
            false_positives = ['Lorem Ipsum', 'John Doe', 'Jane Doe', 'Test User']
            return value not in false_positives
        
        return True
    
    def _remove_overlapping_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove overlapping detections, keeping the one with higher confidence.
        """
        if not detections:
            return detections
        
        # Sort by start position
        sorted_detections = sorted(detections, key=lambda x: x['start'])
        filtered = [sorted_detections[0]]
        
        for current in sorted_detections[1:]:
            last = filtered[-1]
            
            # Check for overlap
            if current['start'] < last['end']:
                # Keep the one with higher confidence
                if current['confidence'] > last['confidence']:
                    filtered[-1] = current
            else:
                filtered.append(current)
        
        return filtered
    
    def anonymize(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """
        Anonymize text by replacing detected sensitive data with placeholders.
        
        Args:
            text: Original text
            detections: List of detections from detect_sensitive_data()
            
        Returns:
            Anonymized text with placeholders
        """
        if not detections:
            return text
        
        # Sort detections by start position in reverse order
        # This ensures indices remain valid as we replace from end to beginning
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        
        anonymized_text = text
        
        for detection in sorted_detections:
            start = detection['start']
            end = detection['end']
            data_type = detection['type']
            
            placeholder = f"[{data_type}]"
            
            # Replace the sensitive data with placeholder
            anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]
            
            logger.debug(f"Replaced {detection['value']} with {placeholder}")
        
        logger.info(f"Anonymized {len(sorted_detections)} sensitive data items")
        return anonymized_text
    
    def get_anonymization_stats(self, detections: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get statistics about detected data types.
        """
        stats = {}
        for detection in detections:
            data_type = detection['type']
            stats[data_type] = stats.get(data_type, 0) + 1
        return stats