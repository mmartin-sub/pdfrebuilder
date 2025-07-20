Batch Processing
================

This guide covers efficient processing of multiple documents using the Multi-Format Document Engine.

Overview
--------

Batch processing allows you to process multiple documents automatically with consistent settings and error handling.

Basic Batch Processing
----------------------

Simple Batch Script
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor
   import os

   def process_directory(input_dir, output_dir):
       processor = BatchProcessor(
           input_directory=input_dir,
           output_directory=output_dir,
           file_pattern="*.pdf"
       )

       results = processor.process_all()

       for result in results:
           if result.success:
               print(f"✓ Processed: {result.filename}")
           else:
               print(f"✗ Failed: {result.filename} - {result.error}")

Command Line Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Process all PDFs in a directory
   hatch run python scripts/batch_process.py --input input/ --output output/

   # Process with specific configuration
   hatch run python scripts/batch_process.py \
       --input input/ \
       --output output/ \
       --config batch_config.json \
       --workers 4

Advanced Batch Configuration
-----------------------------

Parallel Processing
~~~~~~~~~~~~~~~~~~~

Configure parallel processing for better performance:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor, BatchConfig

   config = BatchConfig(
       parallel_workers=4,
       max_memory_per_worker="1GB",
       timeout_per_document=300,  # 5 minutes
       retry_failed=True,
       retry_count=2
   )

   processor = BatchProcessor(
       input_directory="input/",
       output_directory="output/",
       config=config
   )

Filtering and Selection
~~~~~~~~~~~~~~~~~~~~~~~

Process only specific types of documents:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor
   import os

   def custom_filter(filepath):
       # Only process files larger than 1MB
       return os.path.getsize(filepath) > 1024*1024

   processor = BatchProcessor(
       input_directory="input/",
       output_directory="output/",
       file_filter=custom_filter,
       file_pattern="*.pdf"
   )

Error Handling and Logging
---------------------------

Comprehensive Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor
   from pdfrebuilder.exceptions import ProcessingError
   import logging

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('batch_processing.log'),
           logging.StreamHandler()
       ]
   )

   def process_with_error_handling():
       processor = BatchProcessor(
           input_directory="input/",
           output_directory="output/",
           continue_on_error=True
       )

       results = processor.process_all()

       # Generate summary report
       successful = sum(1 for r in results if r.success)
       failed = len(results) - successful

       logging.info(f"Batch processing complete: {successful} successful, {failed} failed")

       # Save failed files list
       failed_files = [r.filename for r in results if not r.success]
       if failed_files:
           with open("failed_files.txt", "w") as f:
               f.write("\n".join(failed_files))

Progress Monitoring
~~~~~~~~~~~~~~~~~~~

Monitor batch processing progress:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor
   from tqdm import tqdm

   def process_with_progress():
       processor = BatchProcessor(
           input_directory="input/",
           output_directory="output/"
       )

       files = processor.get_file_list()

       with tqdm(total=len(files), desc="Processing documents") as pbar:
           for result in processor.process_iterator():
               pbar.set_description(f"Processing {result.filename}")
               pbar.update(1)

               if not result.success:
                   tqdm.write(f"Failed: {result.filename} - {result.error}")

Configuration Templates
-----------------------

Batch Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~

Create a batch_config.json for consistent processing:

.. code-block:: json

   {
     "processing": {
       "parallel_workers": 4,
       "timeout_per_document": 300,
       "memory_limit_per_worker": "1GB"
     },
     "output": {
       "preserve_directory_structure": true,
       "overwrite_existing": false,
       "create_backup": true
     },
     "error_handling": {
       "continue_on_error": true,
       "retry_failed": true,
       "retry_count": 2,
       "log_level": "INFO"
     },
     "validation": {
       "enable_validation": true,
       "similarity_threshold": 0.9,
       "save_validation_reports": true
     }
   }

Quality Assurance
-----------------

Batch Validation
~~~~~~~~~~~~~~~~~

Validate all processed documents:

.. code-block:: python

   from pdfrebuilder.engine import BatchValidator

   def validate_batch_results():
       validator = BatchValidator(
           original_directory="input/",
           processed_directory="output/",
           threshold=0.9
       )

       validation_results = validator.validate_all()

       # Generate quality report
       low_quality = [r for r in validation_results if r.similarity < 0.9]

       if low_quality:
           print(f"Warning: {len(low_quality)} documents below quality threshold")
           for result in low_quality:
               print(f"  {result.filename}: {result.similarity:.2%}")

Performance Optimization
-------------------------

Resource Management
~~~~~~~~~~~~~~~~~~~

Optimize resource usage for large batches:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor, ResourceConfig

   # Configure for large batch processing
   resource_config = ResourceConfig(
       max_concurrent_files=2,
       memory_cleanup_interval=10,  # Clean up every 10 files
       temp_directory="/tmp/batch_processing",
       cleanup_temp_files=True
   )

   processor = BatchProcessor(
       input_directory="large_batch/",
       output_directory="output/",
       resource_config=resource_config
   )

Scheduling and Automation
-------------------------

Automated Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up automated batch processing:

.. code-block:: python

   import schedule
   import time
   from pdfrebuilder.engine import BatchProcessor

   def scheduled_batch_job():
       processor = BatchProcessor(
           input_directory="incoming/",
           output_directory="processed/",
           move_processed_files="archive/"
       )

       results = processor.process_all()
       print(f"Processed {len(results)} files")

   # Schedule to run every hour
   schedule.every().hour.do(scheduled_batch_job)

   while True:
       schedule.run_pending()
       time.sleep(60)

Integration Examples
--------------------

Docker Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   VOLUME ["/input", "/output"]

   CMD ["python", "scripts/batch_process.py", "--input", "/input", "--output", "/output"]

Cloud Processing
~~~~~~~~~~~~~~~~

Process documents in cloud environments:

.. code-block:: python

   import boto3
   from pdfrebuilder.engine import BatchProcessor

   def process_s3_bucket():
       s3 = boto3.client('s3')

       # Download files from S3
       bucket_name = "document-processing"
       local_input = "/tmp/input"
       local_output = "/tmp/output"

       # Process locally
       processor = BatchProcessor(
           input_directory=local_input,
           output_directory=local_output
       )

       results = processor.process_all()

       # Upload results back to S3
       for result in results:
           if result.success:
               s3.upload_file(
                   result.output_path,
                   bucket_name,
                   f"processed/{result.filename}"
               )
