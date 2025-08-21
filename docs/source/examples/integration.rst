Integration Examples
====================

This section demonstrates how to integrate the Multi-Format Document Engine with various systems and workflows.

CI/CD Integration
-----------------

GitHub Actions Workflow
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/document-processing.yml
   name: Document Processing Pipeline

   on:
     push:
       paths:
         - 'documents/**/*.pdf'
     pull_request:
       paths:
         - 'documents/**/*.pdf'

   jobs:
     process-documents:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'

         - name: Install Hatch
           run: pip install hatch

         - name: Create environment
           run: hatch env create

         - name: Process documents
           run: |
             hatch run python scripts/ci_document_processor.py \
               --input documents/ \
               --output processed/ \
               --quality-threshold 0.9

         - name: Upload processed documents
           uses: actions/upload-artifact@v3
           with:
             name: processed-documents
             path: processed/

         - name: Generate quality report
           run: |
             hatch run python scripts/generate_quality_report.py \
               --input documents/ \
               --processed processed/ \
               --output quality_report.html

         - name: Upload quality report
           uses: actions/upload-artifact@v3
           with:
             name: quality-report
             path: quality_report.html

CI Processing Script
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   """
   CI/CD document processing script
   """

   import argparse
   import os
   import sys
   import json
   from pathlib import Path
   from pdfrebuilder.engine import BatchProcessor, VisualValidator

   def main():
       parser = argparse.ArgumentParser(description='Process documents in CI/CD')
       parser.add_argument('--input', required=True, help='Input directory')
       parser.add_argument('--output', required=True, help='Output directory')
       parser.add_argument('--quality-threshold', type=float, default=0.9,
                          help='Minimum quality threshold')
       parser.add_argument('--fail-on-low-quality', action='store_true',
                          help='Fail build if quality is below threshold')

       args = parser.parse_args()

       # Process documents
       processor = BatchProcessor(
           input_directory=args.input,
           output_directory=args.output,
           parallel_workers=2  # Conservative for CI
       )

       results = processor.process_all()

       # Validate quality
       validator = VisualValidator()
       quality_issues = []

       for result in results:
           if result.success:
               original_path = result.input_path
               processed_path = result.output_path

               validation = validator.compare_documents(original_path, processed_path)

               if validation.similarity < args.quality_threshold:
                   quality_issues.append({
                       'file': result.filename,
                       'similarity': validation.similarity,
                       'threshold': args.quality_threshold
                   })

       # Generate summary
       summary = {
           'total_files': len(results),
           'successful': sum(1 for r in results if r.success),
           'failed': sum(1 for r in results if not r.success),
           'quality_issues': len(quality_issues),
           'average_quality': sum(r.get('similarity', 0) for r in results) / len(results) if results else 0
       }

       print(f"Processing Summary:")
       print(f"  Total files: {summary['total_files']}")
       print(f"  Successful: {summary['successful']}")
       print(f"  Failed: {summary['failed']}")
       print(f"  Quality issues: {summary['quality_issues']}")
       print(f"  Average quality: {summary['average_quality']:.2%}")

       # Save summary for artifacts
       with open('processing_summary.json', 'w') as f:
           json.dump(summary, f, indent=2)

       # Exit with error if quality issues and fail flag is set
       if quality_issues and args.fail_on_low_quality:
           print("Quality issues detected:")
           for issue in quality_issues:
               print(f"  {issue['file']}: {issue['similarity']:.2%} < {issue['threshold']:.2%}")
           sys.exit(1)

       print("✓ All documents processed successfully")

   if __name__ == '__main__':
       main()

Docker Integration
------------------

Dockerfile
~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       libffi-dev \
       libssl-dev \
       && rm -rf /var/lib/apt/lists/*

   # Set working directory
   WORKDIR /app

   # Install Hatch
   RUN pip install hatch

   # Copy project files
   COPY pyproject.toml .
   COPY src/ src/
   COPY scripts/ scripts/

   # Create Hatch environment
   RUN hatch env create

   # Create directories
   RUN mkdir -p /input /output /config

   # Set volumes
   VOLUME ["/input", "/output", "/config"]

   # Default command
   CMD ["hatch", "run", "python", "scripts/docker_processor.py"]

Docker Compose Setup
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'

   services:
     document-processor:
       build: .
       volumes:
         - ./input:/input
         - ./output:/output
         - ./config:/config
       environment:
         - PROCESSING_MODE=batch
         - QUALITY_THRESHOLD=0.9
         - PARALLEL_WORKERS=4
       restart: unless-stopped

     document-api:
       build: .
       command: hatch run python scripts/api_server.py
       ports:
         - "8080:8080"
       volumes:
         - ./temp:/tmp
       environment:
         - API_MODE=true
         - MAX_FILE_SIZE=50MB
       restart: unless-stopped

     redis:
       image: redis:alpine
       ports:
         - "6379:6379"
       restart: unless-stopped

     worker:
       build: .
       command: hatch run python scripts/worker.py
       depends_on:
         - redis
       environment:
         - REDIS_URL=redis://redis:6379
         - WORKER_CONCURRENCY=2
       restart: unless-stopped
       deploy:
         replicas: 3

Kubernetes Deployment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # k8s-deployment.yml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: document-processor
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: document-processor
     template:
       metadata:
         labels:
           app: document-processor
       spec:
         containers:
         - name: processor
           image: document-processor:latest
           resources:
             requests:
               memory: "1Gi"
               cpu: "500m"
             limits:
               memory: "2Gi"
               cpu: "1000m"
           env:
           - name: PROCESSING_MODE
             value: "api"
           - name: REDIS_URL
             value: "redis://redis-service:6379"
           ports:
           - containerPort: 8080
           volumeMounts:
           - name: temp-storage
             mountPath: /tmp
         volumes:
         - name: temp-storage
           emptyDir:
             sizeLimit: 10Gi

   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: document-processor-service
   spec:
     selector:
       app: document-processor
     ports:
     - port: 80
       targetPort: 8080
     type: LoadBalancer

Cloud Integration
-----------------

AWS Lambda Function
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   import boto3
   import tempfile
   import os
   from pdfrebuilder.engine import DocumentEngine

   def lambda_handler(event, context):
       """
       AWS Lambda function for document processing
       """

       s3 = boto3.client('s3')
       engine = DocumentEngine()

       try:
           # Get S3 bucket and key from event
           bucket = event['Records'][0]['s3']['bucket']['name']
           key = event['Records'][0]['s3']['object']['key']

           # Download file from S3
           with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_input:
               s3.download_fileobj(bucket, key, tmp_input)
               tmp_input.flush()

               # Process document
               layout = engine.extract(tmp_input.name)

               # Generate processed document
               with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_output:
                   engine.rebuild(layout, tmp_output.name)

                   # Upload processed document
                   output_key = f"processed/{key}"
                   s3.upload_file(tmp_output.name, bucket, output_key)

                   # Upload layout configuration
                   config_key = f"configs/{key}.json"
                   s3.put_object(
                       Bucket=bucket,
                       Key=config_key,
                       Body=json.dumps(layout, indent=2),
                       ContentType='application/json'
                   )

           return {
               'statusCode': 200,
               'body': json.dumps({
                   'message': 'Document processed successfully',
                   'input_key': key,
                   'output_key': output_key,
                   'config_key': config_key
               })
           }

       except Exception as e:
           print(f"Error processing document: {e}")
           return {
               'statusCode': 500,
               'body': json.dumps({
                   'error': str(e)
               })
           }

Google Cloud Function
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import functions_framework
   from google.cloud import storage
   import tempfile
   import json
   from pdfrebuilder.engine import DocumentEngine

   @functions_framework.cloud_event
   def process_document(cloud_event):
       """
       Google Cloud Function triggered by Cloud Storage
       """

       data = cloud_event.data
       bucket_name = data['bucket']
       file_name = data['name']

       if not file_name.endswith('.pdf'):
           print(f"Skipping non-PDF file: {file_name}")
           return

       storage_client = storage.Client()
       bucket = storage_client.bucket(bucket_name)

       engine = DocumentEngine()

       try:
           # Download file
           blob = bucket.blob(file_name)

           with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_input:
               blob.download_to_filename(tmp_input.name)

               # Process document
               layout = engine.extract(tmp_input.name)

               # Generate processed document
               with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_output:
                   engine.rebuild(layout, tmp_output.name)

                   # Upload processed document
                   output_blob = bucket.blob(f"processed/{file_name}")
                   output_blob.upload_from_filename(tmp_output.name)

                   # Upload configuration
                   config_blob = bucket.blob(f"configs/{file_name}.json")
                   config_blob.upload_from_string(
                       json.dumps(layout, indent=2),
                       content_type='application/json'
                   )

           print(f"Successfully processed: {file_name}")

       except Exception as e:
           print(f"Error processing {file_name}: {e}")
           raise

Database Integration
--------------------

PostgreSQL Integration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psycopg2
   import json
   from datetime import datetime
   from pdfrebuilder.engine import DocumentEngine, VisualValidator

   class DocumentDatabase:
       def __init__(self, connection_string):
           self.conn = psycopg2.connect(connection_string)
           self.engine = DocumentEngine()
           self.validator = VisualValidator()
           self.setup_tables()

       def setup_tables(self):
           cursor = self.conn.cursor()

           # Create documents table
           cursor.execute("""
               CREATE TABLE IF NOT EXISTS documents (
                   id SERIAL PRIMARY KEY,
                   filename VARCHAR(255) NOT NULL,
                   original_path TEXT NOT NULL,
                   processed_path TEXT,
                   layout_config JSONB,
                   processing_status VARCHAR(50) DEFAULT 'pending',
                   quality_score FLOAT,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   processed_at TIMESTAMP,
                   error_message TEXT
               )
           """)

           # Create processing_jobs table
           cursor.execute("""
               CREATE TABLE IF NOT EXISTS processing_jobs (
                   id SERIAL PRIMARY KEY,
                   document_id INTEGER REFERENCES documents(id),
                   job_type VARCHAR(50) NOT NULL,
                   status VARCHAR(50) DEFAULT 'queued',
                   started_at TIMESTAMP,
                   completed_at TIMESTAMP,
                   result JSONB,
                   error_message TEXT
               )
           """)

           self.conn.commit()
           cursor.close()

       def add_document(self, filename, original_path):
           cursor = self.conn.cursor()

           cursor.execute("""
               INSERT INTO documents (filename, original_path)
               VALUES (%s, %s)
               RETURNING id
           """, (filename, original_path))

           document_id = cursor.fetchone()[0]
           self.conn.commit()
           cursor.close()

           return document_id

       def process_document(self, document_id, output_path):
           cursor = self.conn.cursor()

           try:
               # Get document info
               cursor.execute("""
                   SELECT filename, original_path FROM documents WHERE id = %s
               """, (document_id,))

               filename, original_path = cursor.fetchone()

               # Update status
               cursor.execute("""
                   UPDATE documents
                   SET processing_status = 'processing'
                   WHERE id = %s
               """, (document_id,))
               self.conn.commit()

               # Process document
               layout = self.engine.extract(original_path)
               self.engine.rebuild(layout, output_path)

               # Validate quality
               validation = self.validator.compare_documents(original_path, output_path)

               # Update database
               cursor.execute("""
                   UPDATE documents
                   SET processed_path = %s,
                       layout_config = %s,
                       processing_status = 'completed',
                       quality_score = %s,
                       processed_at = %s
                   WHERE id = %s
               """, (
                   output_path,
                   json.dumps(layout),
                   validation.similarity,
                   datetime.now(),
                   document_id
               ))

               self.conn.commit()

               return {
                   'success': True,
                   'quality_score': validation.similarity
               }

           except Exception as e:
               # Update error status
               cursor.execute("""
                   UPDATE documents
                   SET processing_status = 'failed',
                       error_message = %s
                   WHERE id = %s
               """, (str(e), document_id))

               self.conn.commit()

               return {
                   'success': False,
                   'error': str(e)
               }

           finally:
               cursor.close()

       def get_processing_stats(self):
           cursor = self.conn.cursor()

           cursor.execute("""
               SELECT
                   processing_status,
                   COUNT(*) as count,
                   AVG(quality_score) as avg_quality
               FROM documents
               GROUP BY processing_status
           """)

           stats = {}
           for status, count, avg_quality in cursor.fetchall():
               stats[status] = {
                   'count': count,
                   'average_quality': float(avg_quality) if avg_quality else None
               }

           cursor.close()
           return stats

Message Queue Integration
-------------------------

Celery Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from celery import Celery
   from pdfrebuilder.engine import DocumentEngine, VisualValidator
   import os
   import json

   # Configure Celery
   app = Celery('document_processor')
   app.config_from_object({
       'broker_url': 'redis://localhost:6379/0',
       'result_backend': 'redis://localhost:6379/0',
       'task_serializer': 'json',
       'accept_content': ['json'],
       'result_serializer': 'json',
       'timezone': 'UTC',
       'enable_utc': True,
   })

   @app.task(bind=True)
   def process_document_task(self, input_path, output_path, options=None):
       """
       Celery task for document processing
       """

       try:
           # Update task state
           self.update_state(
               state='PROCESSING',
               meta={'status': 'Starting document processing'}
           )

           engine = DocumentEngine()

           # Extract layout
           self.update_state(
               state='PROCESSING',
               meta={'status': 'Extracting document layout'}
           )

           layout = engine.extract(input_path)

           # Apply options if provided
           if options:
               if options.get('use_template_mode'):
                   # Re-extract with template mode
                   layout = engine.extract(input_path, use_template=True)

           # Rebuild document
           self.update_state(
               state='PROCESSING',
               meta={'status': 'Rebuilding document'}
           )

           engine.rebuild(layout, output_path)

           # Validate quality
           self.update_state(
               state='PROCESSING',
               meta={'status': 'Validating quality'}
           )

           validator = VisualValidator()
           validation = validator.compare_documents(input_path, output_path)

           return {
               'status': 'completed',
               'output_path': output_path,
               'quality_score': validation.similarity,
               'processing_time': self.request.time_limit
           }

       except Exception as e:
           self.update_state(
               state='FAILURE',
               meta={'error': str(e)}
           )
           raise

   @app.task
   def batch_process_documents(input_directory, output_directory):
       """
       Celery task for batch processing
       """

       pdf_files = [f for f in os.listdir(input_directory) if f.endswith('.pdf')]

       # Create subtasks
       job_group = []
       for filename in pdf_files:
           input_path = os.path.join(input_directory, filename)
           output_path = os.path.join(output_directory, f"processed_{filename}")

           task = process_document_task.delay(input_path, output_path)
           job_group.append({
               'filename': filename,
               'task_id': task.id
           })

       return {
           'batch_id': f"batch_{len(job_group)}_files",
           'jobs': job_group
       }

   # Worker startup
   if __name__ == '__main__':
       app.start()

RabbitMQ Integration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pika
   import json
   import threading
   from pdfrebuilder.engine import DocumentEngine

   class DocumentProcessorWorker:
       def __init__(self, rabbitmq_url='amqp://localhost'):
           self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
           self.channel = self.connection.channel()
           self.engine = DocumentEngine()

           # Declare queues
           self.channel.queue_declare(queue='document_processing', durable=True)
           self.channel.queue_declare(queue='processing_results', durable=True)

           # Set QoS to process one message at a time
           self.channel.basic_qos(prefetch_count=1)

       def process_message(self, ch, method, properties, body):
           try:
               # Parse message
               message = json.loads(body)

               input_path = message['input_path']
               output_path = message['output_path']
               job_id = message['job_id']

               print(f"Processing job {job_id}: {input_path}")

               # Process document
               layout = self.engine.extract(input_path)
               self.engine.rebuild(layout, output_path)

               # Send result
               result = {
                   'job_id': job_id,
                   'status': 'completed',
                   'output_path': output_path
               }

               self.channel.basic_publish(
                   exchange='',
                   routing_key='processing_results',
                   body=json.dumps(result),
                   properties=pika.BasicProperties(delivery_mode=2)  # Persistent
               )

               print(f"Completed job {job_id}")

           except Exception as e:
               # Send error result
               error_result = {
                   'job_id': message.get('job_id', 'unknown'),
                   'status': 'failed',
                   'error': str(e)
               }

               self.channel.basic_publish(
                   exchange='',
                   routing_key='processing_results',
                   body=json.dumps(error_result),
                   properties=pika.BasicProperties(delivery_mode=2)
               )

               print(f"Failed job {message.get('job_id', 'unknown')}: {e}")

           finally:
               # Acknowledge message
               ch.basic_ack(delivery_tag=method.delivery_tag)

       def start_consuming(self):
           self.channel.basic_consume(
               queue='document_processing',
               on_message_callback=self.process_message
           )

           print("Worker started. Waiting for messages...")
           self.channel.start_consuming()

       def stop_consuming(self):
           self.channel.stop_consuming()
           self.connection.close()

   # Publisher class
   class DocumentProcessorPublisher:
       def __init__(self, rabbitmq_url='amqp://localhost'):
           self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
           self.channel = self.connection.channel()

           # Declare queues
           self.channel.queue_declare(queue='document_processing', durable=True)

       def submit_job(self, input_path, output_path, job_id):
           message = {
               'job_id': job_id,
               'input_path': input_path,
               'output_path': output_path
           }

           self.channel.basic_publish(
               exchange='',
               routing_key='document_processing',
               body=json.dumps(message),
               properties=pika.BasicProperties(delivery_mode=2)  # Persistent
           )

           print(f"Submitted job {job_id}")

       def close(self):
           self.connection.close()

   if __name__ == '__main__':
       worker = DocumentProcessorWorker()
       try:
           worker.start_consuming()
       except KeyboardInterrupt:
           print("Stopping worker...")
           worker.stop_consuming()
