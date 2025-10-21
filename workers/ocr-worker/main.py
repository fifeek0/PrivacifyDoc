import pika
import os
import json
import io
import time
import ocrProcessor

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
    channel.queue_declare(queue='document.uploaded', durable=True)
    channel.queue_declare(queue='text.extracted', durable=True)
    print("RabbitMQ queues are set up.")

def on_message_received(ch, method, properties, body):
    """Callback function to process messages from the upload queue."""
    message = json.loads(body)
    document_id = message.get('documentId')
    file_path = message.get('filePath') # Assuming the API provides the path to the stored file

    print(f"Received document {document_id} for OCR processing from path: {file_path}")

    try:
        # In a real scenario, you'd use a shared volume or download the file.
        # For now, we'll assume the API and workers share a filesystem.
        with open(file_path, 'rb') as f:
            # The process_ocr function needs a file-like object
            file_like_object = io.BytesIO(f.read())
            extracted_text = ocrProcessor.process_ocr(file_like_object)

        # Prepare the result message
        result_message = {
            'documentId': document_id,
            'text': extracted_text
        }

        # Publish the results to the text extraction completion queue
        ch.basic_publish(
            exchange='',
            routing_key='text.extracted',
            body=json.dumps(result_message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(f"Finished OCR for document {document_id}. Text extracted and sent for anonymization.")

    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        # Optionally, publish to an error queue

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Main function to start the OCR service."""
    print("Starting OCR Service...")
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    setup_queues(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='document.uploaded', on_message_callback=on_message_received)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    main()
