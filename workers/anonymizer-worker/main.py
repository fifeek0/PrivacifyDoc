import pika
import os
import json
import time
import logging
from anonymizer import PatternBasedAnonymizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_rabbitmq_connection():
    """Establishes a connection to RabbitMQ, retrying if necessary."""
    rabbitmq_host = os.environ.get('RabbitMQ__HostName', 'localhost')
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            print("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def setup_queues(channel):
    """Declares the necessary RabbitMQ queues."""
    channel.queue_declare(queue='text.extracted', durable=True)
    channel.queue_declare(queue='document.anonymized', durable=True)
    logger.info("RabbitMQ queues are set up.")

def process_document_anonymization(text: str, file_path: str) -> tuple:
    """
    Process document anonymization using pattern-based detection.
    
    Args:
        text: Extracted text from OCR
        file_path: Path to original file
        
    Returns:
        tuple: (anonymized_file_path, detected_data_list)
    """
    logger.info("Starting pattern-based anonymization...")
    
    try:
        # Initialize anonymizer
        anonymizer = PatternBasedAnonymizer()
        
        # Detect sensitive data
        detections = anonymizer.detect_sensitive_data(text)
        logger.info(f"Detected {len(detections)} sensitive data items")
        
        # Anonymize text
        anonymized_text = anonymizer.anonymize(text, detections)
        
        # Save anonymized file
        anonymized_file_path = file_path.replace('/app/files/', '/app/files/anonymized_')
        with open(anonymized_file_path, 'w', encoding='utf-8') as f:
            f.write(anonymized_text)
        
        logger.info(f"Anonymized file saved to: {anonymized_file_path}")
        
        # Convert detections to expected format
        detected_data = []
        for detection in detections:
            detected_data.append({
                'type': detection['type'],
                'originalValue': detection['value'],
                'startPosition': detection['start'],
                'endPosition': detection['end'],
                'confidence': detection['confidence']
            })
        
        return anonymized_file_path, detected_data
        
    except Exception as e:
        logger.error(f"Error during anonymization: {e}")
        raise

def on_message_received(ch, method, properties, body):
    """Callback function to process messages from the OCR queue."""
    correlation_id = f"anon-{int(time.time())}"
    
    try:
        message = json.loads(body)
        document_id = message.get('documentId')
        extracted_text = message.get('extractedText')
        page_count = message.get('pageCount', 1)
        
        logger.info(f"Received document {document_id} for anonymization | CorrelationId: {correlation_id}")
        
        if not extracted_text:
            logger.warning(f"No text provided for document {document_id} | CorrelationId: {correlation_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Process anonymization
        # Note: For now we'll create a simple text file, later this should handle the original file format
        original_file_path = f"/app/files/document_{document_id}.txt"
        
        anonymized_file_path, detected_data = process_document_anonymization(
            extracted_text, 
            original_file_path
        )
        
        # Prepare the result message in the expected format
        result_message = {
            'documentId': document_id,
            'anonymizedFilePath': anonymized_file_path,
            'detectedData': detected_data,
            'anonymizedAt': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        
        # Publish the results to the completion queue
        ch.basic_publish(
            exchange='',
            routing_key='document.anonymized',
            body=json.dumps(result_message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            ))
        
        logger.info(f"Finished processing document {document_id}. Found {len(detected_data)} sensitive items | CorrelationId: {correlation_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing document: {e} | CorrelationId: {correlation_id}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Main function to start the anonymizer service."""
    logger.info("Starting Pattern-Based Anonymizer Service...")
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    setup_queues(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='text.extracted', on_message_callback=on_message_received)

    logger.info("Waiting for messages from 'text.extracted' queue. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping anonymizer service...")
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    main()
