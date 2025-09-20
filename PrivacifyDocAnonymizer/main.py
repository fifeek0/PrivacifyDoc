import pika
import os
import json
import ollama
import time

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
    channel.queue_declare(queue='document_ocr_completed', durable=True)
    channel.queue_declare(queue='document_anonymization_completed', durable=True)
    print("RabbitMQ queues are set up.")

def detect_sensitive_data(text):
    """ 
    Placeholder function to detect sensitive data using a local AI model.
    This is where you will integrate Ollama or another model.
    """
    print("Detecting sensitive data with local AI model...")
    try:
        # Example: Using Ollama to find names, emails, and phone numbers
        # You will need to refine the prompt for your specific needs.
        response = ollama.chat(
            model='qwen:latest', # Or your model of choice
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert at finding sensitive data in text. Respond with only a JSON array of objects. Each object should have "type" and "value" keys. Supported types are: PersonName, Email, PhoneNumber, PESEL, NIP, Address.',
                },
                {
                    'role': 'user',
                    'content': f'Find all sensitive data in the following text: \n\n{text}',
                },
            ]
        )
        
        # The response content should be a JSON string, so we parse it.
        detected_data = json.loads(response['message']['content'])
        print(f"Detected data: {detected_data}")
        return detected_data
    except Exception as e:
        print(f"Error during AI-based data detection: {e}")
        return []

def on_message_received(ch, method, properties, body):
    """Callback function to process messages from the OCR queue."""
    message = json.loads(body)
    document_id = message.get('documentId')
    document_text = message.get('text')

    print(f"Received document {document_id} for anonymization.")

    # 1. Detect sensitive data using the AI model
    sensitive_data = detect_sensitive_data(document_text)

    # 2. Prepare the result message
    result_message = {
        'documentId': document_id,
        'detectedData': sensitive_data
    }

    # 3. Publish the results to the completion queue
    ch.basic_publish(
        exchange='',
        routing_key='document_anonymization_completed',
        body=json.dumps(result_message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))

    print(f"Finished processing document {document_id}. Results sent.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Main function to start the anonymizer service."""
    print("Starting Anonymizer Service...")
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    setup_queues(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='document_ocr_completed', on_message_callback=on_message_received)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    main()
