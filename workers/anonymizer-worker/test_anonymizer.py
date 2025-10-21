#!/usr/bin/env python3
"""
Test script for PatternBasedAnonymizer
Demonstrates detection and anonymization of Polish sensitive data.
"""

from anonymizer import PatternBasedAnonymizer

def test_anonymizer():
    """Test the pattern-based anonymizer with sample Polish text."""
    
    test_text = """
Jan Kowalski
ul. Kwiatowa 15
00-001 Warszawa
jan.kowalski@example.com
+48 123 456 789
PESEL: 92010112345
NIP: 1234567890
REGON: 123456789

Anna Nowak mieszka przy al. Jerozolimskie 100, kod pocztowy 02-001.
Jej telefon to 48 987 654 321, a email: anna.nowak@firma.pl
PESEL: 85030298765
NIP: 9876543210

Firma XYZ Sp. z o.o.
os. Słoneczne 5/10
31-123 Kraków
kontakt@xyz.com.pl
REGON: 987654321012345
"""

    print("=== TESTING PATTERN-BASED ANONYMIZER ===\n")
    print("Original text:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    # Initialize anonymizer
    anonymizer = PatternBasedAnonymizer()
    
    # Detect sensitive data
    print("DETECTION PHASE:")
    detections = anonymizer.detect_sensitive_data(test_text)
    
    print(f"Found {len(detections)} sensitive data items:\n")
    for i, detection in enumerate(detections, 1):
        print(f"{i}. {detection['type']}: '{detection['value']}' "
              f"(confidence: {detection['confidence']}, "
              f"position: {detection['start']}-{detection['end']})")
    
    print("\n" + "="*50 + "\n")
    
    # Get statistics
    stats = anonymizer.get_anonymization_stats(detections)
    print("DETECTION STATISTICS:")
    for data_type, count in stats.items():
        print(f"- {data_type}: {count} items")
    
    print("\n" + "="*50 + "\n")
    
    # Anonymize text
    print("ANONYMIZATION PHASE:")
    anonymized_text = anonymizer.anonymize(test_text, detections)
    
    print("Anonymized text:")
    print(anonymized_text)
    
    print("\n" + "="*50 + "\n")
    
    # Verify anonymization
    print("VERIFICATION:")
    sensitive_items = [
        "92010112345", "85030298765",  # PESELs
        "jan.kowalski@example.com", "anna.nowak@firma.pl", "kontakt@xyz.com.pl",  # Emails
        "1234567890", "9876543210",  # NIPs
        "+48 123 456 789", "48 987 654 321"  # Phones
    ]
    
    found_sensitive = []
    for item in sensitive_items:
        if item in anonymized_text:
            found_sensitive.append(item)
    
    if found_sensitive:
        print(f"❌ FAILED: Found {len(found_sensitive)} sensitive items still present:")
        for item in found_sensitive:
            print(f"  - {item}")
    else:
        print("✅ SUCCESS: No sensitive data found in anonymized text")
    
    # Check placeholders
    expected_placeholders = ["[PESEL]", "[EMAIL]", "[NIP]", "[PHONE]", "[PERSON_NAME]", "[ADDRESS]"]
    found_placeholders = []
    for placeholder in expected_placeholders:
        if placeholder in anonymized_text:
            found_placeholders.append(placeholder)
    
    print(f"\nPlaceholders found: {found_placeholders}")
    print(f"Expected at least: [PESEL], [EMAIL], [NIP], [PHONE]")
    
    return len(found_sensitive) == 0 and len(found_placeholders) >= 4

if __name__ == "__main__":
    success = test_anonymizer()
    print(f"\n{'='*50}")
    print(f"TEST RESULT: {'PASSED' if success else 'FAILED'}")
    print(f"{'='*50}")