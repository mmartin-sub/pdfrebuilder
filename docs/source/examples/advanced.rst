Advanced Examples
=================

This section contains complex usage examples demonstrating advanced features of the Multi-Format Document Engine.

Multi-Engine Processing
-----------------------

Engine Selection and Fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import PDFEngineSelector, DocumentEngine
   from pdfrebuilder.exceptions import ProcessingError

   def process_with_fallback(input_file, output_file):
       selector = PDFEngineSelector()

       # Try optimal engine first
       try:
           optimal_engine = selector.get_optimal_engine(
               document_path=input_file,
               requirements=["high_quality", "text_extraction", "image_processing"]
           )

           engine = DocumentEngine(pdf_engine=optimal_engine)
           layout = engine.extract(input_file)
           engine.rebuild(layout, output_file)

           print(f"✓ Processed with {optimal_engine.__class__.__name__}")
           return True

       except ProcessingError as e:
           print(f"Primary engine failed: {e}")

           # Fallback to template mode
           try:
               fallback_engine = selector.get_fallback_engine()
               engine = DocumentEngine(pdf_engine=fallback_engine)
               layout = engine.extract(input_file, use_template=True)
               engine.rebuild(layout, output_file)

               print(f"✓ Processed with fallback engine in template mode")
               return True

           except Exception as e:
               print(f"✗ All processing methods failed: {e}")
               return False

Custom Engine Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import PyMuPDFEngine, ReportLabEngine, EngineConfig

   class CustomProcessingPipeline:
       def __init__(self):
           # Configure extraction engine
           self.extraction_config = EngineConfig(
               text_extraction_mode="precise",
               image_extraction_quality="high",
               preserve_vector_graphics=True,
               font_embedding_mode="subset"
           )

           # Configure rendering engine
           self.rendering_config = EngineConfig(
               output_quality="maximum",
               color_space="RGB",
               compression_level="medium",
               font_optimization=True
           )

           self.extractor = PyMuPDFEngine(config=self.extraction_config)
           self.renderer = ReportLabEngine(config=self.rendering_config)

       def process_document(self, input_file, output_file):
           # Extract with PyMuPDF
           layout = self.extractor.extract(input_file)

           # Apply custom transformations
           layout = self.apply_custom_transformations(layout)

           # Render with ReportLab
           self.renderer.rebuild(layout, output_file)

       def apply_custom_transformations(self, layout):
           # Custom processing logic
           for page in layout['document_structure']:
               for element in page['layers'][0]['content']:
                   if element['type'] == 'text':
                       # Apply custom text processing
                       element = self.enhance_text_element(element)
                   elif element['type'] == 'image':
                       # Apply custom image processing
                       element = self.enhance_image_element(element)

           return layout

Complex Document Analysis
-------------------------

Document Structure Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentAnalyzer, StructureDetector
   import json

   class DocumentStructureAnalyzer:
       def __init__(self):
           self.analyzer = DocumentAnalyzer()
           self.detector = StructureDetector()

       def analyze_document(self, pdf_path):
           # Extract basic layout
           layout = self.analyzer.extract(pdf_path)

           # Detect document structure
           structure = self.detector.detect_structure(layout)

           analysis = {
               'document_type': structure.document_type,
               'page_count': len(layout['document_structure']),
               'text_blocks': self.count_text_blocks(layout),
               'images': self.count_images(layout),
               'tables': structure.tables,
               'headers_footers': structure.headers_footers,
               'columns': structure.column_layout,
               'reading_order': structure.reading_order
           }

           return analysis

       def count_text_blocks(self, layout):
           count = 0
           for page in layout['document_structure']:
               for element in page['layers'][0]['content']:
                   if element['type'] == 'text':
                       count += 1
           return count

       def count_images(self, layout):
           count = 0
           for page in layout['document_structure']:
               for element in page['layers'][0]['content']:
                   if element['type'] == 'image':
                       count += 1
           return count

       def generate_report(self, pdf_path, output_path):
           analysis = self.analyze_document(pdf_path)

           with open(output_path, 'w') as f:
               json.dump(analysis, f, indent=2)

           print(f"Analysis report saved to {output_path}")

Content Extraction and Transformation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import ContentExtractor, TextProcessor, ImageProcessor
   import re

   class IntelligentContentProcessor:
       def __init__(self):
           self.extractor = ContentExtractor()
           self.text_processor = TextProcessor()
           self.image_processor = ImageProcessor()

       def extract_and_transform(self, pdf_path):
           layout = self.extractor.extract(pdf_path)

           # Process each page
           for page_idx, page in enumerate(layout['document_structure']):
               print(f"Processing page {page_idx + 1}")

               # Extract and process text
               text_elements = self.extract_text_elements(page)
               processed_text = self.process_text_content(text_elements)

               # Extract and process images
               image_elements = self.extract_image_elements(page)
               processed_images = self.process_image_content(image_elements)

               # Reconstruct page with processed content
               self.reconstruct_page(page, processed_text, processed_images)

           return layout

       def extract_text_elements(self, page):
           text_elements = []
           for element in page['layers'][0]['content']:
               if element['type'] == 'text':
                   text_elements.append(element)
           return text_elements

       def process_text_content(self, text_elements):
           processed = []

           for element in text_elements:
               # Clean and normalize text
               cleaned_text = self.text_processor.clean_text(element['text'])

               # Detect and correct common OCR errors
               corrected_text = self.text_processor.correct_ocr_errors(cleaned_text)

               # Apply intelligent formatting
               formatted_text = self.text_processor.apply_smart_formatting(corrected_text)

               element['text'] = formatted_text
               processed.append(element)

           return processed

       def process_image_content(self, image_elements):
           processed = []

           for element in image_elements:
               # Enhance image quality
               enhanced_path = self.image_processor.enhance_image(element['image_file'])

               # Update element with enhanced image
               element['image_file'] = enhanced_path
               processed.append(element)

           return processed

Advanced Batch Processing
-------------------------

Intelligent Batch Processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor, QualityAnalyzer
   from concurrent.futures import ThreadPoolExecutor, as_completed
   import os
   import json
   from datetime import datetime

   class IntelligentBatchProcessor:
       def __init__(self, input_dir, output_dir, max_workers=4):
           self.input_dir = input_dir
           self.output_dir = output_dir
           self.max_workers = max_workers
           self.quality_analyzer = QualityAnalyzer()

           # Create output directories
           os.makedirs(output_dir, exist_ok=True)
           os.makedirs(f"{output_dir}/high_quality", exist_ok=True)
           os.makedirs(f"{output_dir}/needs_review", exist_ok=True)
           os.makedirs(f"{output_dir}/failed", exist_ok=True)
           os.makedirs(f"{output_dir}/reports", exist_ok=True)

       def process_batch(self):
           pdf_files = [f for f in os.listdir(self.input_dir) if f.endswith('.pdf')]

           results = {
               'processed': [],
               'failed': [],
               'needs_review': [],
               'statistics': {}
           }

           with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
               # Submit all jobs
               future_to_file = {
                   executor.submit(self.process_single_file, filename): filename
                   for filename in pdf_files
               }

               # Process completed jobs
               for future in as_completed(future_to_file):
                   filename = future_to_file[future]
                   try:
                       result = future.result()
                       self.categorize_result(result, results)
                       print(f"✓ Completed: {filename}")
                   except Exception as e:
                       print(f"✗ Failed: {filename} - {e}")
                       results['failed'].append({
                           'filename': filename,
                           'error': str(e)
                       })

           # Generate summary report
           self.generate_batch_report(results)
           return results

       def process_single_file(self, filename):
           input_path = os.path.join(self.input_dir, filename)

           # Analyze document complexity
           complexity = self.analyze_document_complexity(input_path)

           # Choose processing strategy based on complexity
           if complexity['score'] > 0.8:
               strategy = 'high_precision'
           elif complexity['score'] > 0.5:
               strategy = 'balanced'
           else:
               strategy = 'fast'

           # Process with selected strategy
           result = self.process_with_strategy(input_path, filename, strategy)

           # Validate quality
           quality_score = self.quality_analyzer.analyze(
               input_path,
               result['output_path']
           )

           result['quality_score'] = quality_score
           result['complexity'] = complexity
           result['strategy'] = strategy

           return result

       def analyze_document_complexity(self, pdf_path):
           # Implement complexity analysis
           # This is a simplified version
           return {
               'score': 0.7,  # Placeholder
               'factors': ['complex_graphics', 'multiple_fonts', 'embedded_images']
           }

       def process_with_strategy(self, input_path, filename, strategy):
           from pdfrebuilder.engine import DocumentEngine, ProcessingConfig

           if strategy == 'high_precision':
               config = ProcessingConfig(
                   text_extraction_mode='precise',
                   image_quality='maximum',
                   preserve_vector_graphics=True,
                   use_template_fallback=True
               )
           elif strategy == 'balanced':
               config = ProcessingConfig(
                   text_extraction_mode='balanced',
                   image_quality='high',
                   preserve_vector_graphics=True
               )
           else:  # fast
               config = ProcessingConfig(
                   text_extraction_mode='fast',
                   image_quality='medium',
                   skip_complex_graphics=True
               )

           engine = DocumentEngine(config=config)

           output_path = os.path.join(self.output_dir, f"processed_{filename}")

           layout = engine.extract(input_path)
           engine.rebuild(layout, output_path)

           return {
               'filename': filename,
               'input_path': input_path,
               'output_path': output_path,
               'processing_time': 0,  # Implement timing
               'success': True
           }

       def categorize_result(self, result, results):
           if result['quality_score'] > 0.9:
               # High quality - move to high_quality folder
               new_path = os.path.join(self.output_dir, 'high_quality', result['filename'])
               os.rename(result['output_path'], new_path)
               result['final_path'] = new_path
               results['processed'].append(result)
           elif result['quality_score'] > 0.7:
               # Acceptable quality
               results['processed'].append(result)
           else:
               # Needs review
               review_path = os.path.join(self.output_dir, 'needs_review', result['filename'])
               os.rename(result['output_path'], review_path)
               result['final_path'] = review_path
               results['needs_review'].append(result)

Custom Validation Pipeline
---------------------------

Advanced Quality Assurance
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator, ContentValidator, StructureValidator
   import numpy as np

   class ComprehensiveValidator:
       def __init__(self):
           self.visual_validator = VisualValidator()
           self.content_validator = ContentValidator()
           self.structure_validator = StructureValidator()

       def comprehensive_validation(self, original_path, reconstructed_path):
           results = {}

           # Visual validation
           visual_result = self.visual_validator.compare_documents(
               original_path, reconstructed_path
           )
           results['visual'] = {
               'similarity': visual_result.similarity,
               'text_accuracy': visual_result.text_accuracy,
               'layout_accuracy': visual_result.layout_accuracy,
               'color_accuracy': visual_result.color_accuracy
           }

           # Content validation
           content_result = self.content_validator.validate_content(
               original_path, reconstructed_path
           )
           results['content'] = {
               'text_preservation': content_result.text_preservation,
               'image_preservation': content_result.image_preservation,
               'metadata_preservation': content_result.metadata_preservation
           }

           # Structure validation
           structure_result = self.structure_validator.validate_structure(
               original_path, reconstructed_path
           )
           results['structure'] = {
               'page_count_match': structure_result.page_count_match,
               'element_count_match': structure_result.element_count_match,
               'reading_order_preserved': structure_result.reading_order_preserved
           }

           # Calculate overall score
           results['overall_score'] = self.calculate_overall_score(results)
           results['recommendation'] = self.get_recommendation(results)

           return results

       def calculate_overall_score(self, results):
           weights = {
               'visual': 0.4,
               'content': 0.4,
               'structure': 0.2
           }

           visual_score = np.mean([
               results['visual']['similarity'],
               results['visual']['text_accuracy'],
               results['visual']['layout_accuracy']
           ])

           content_score = np.mean([
               results['content']['text_preservation'],
               results['content']['image_preservation']
           ])

           structure_score = np.mean([
               results['structure']['page_count_match'],
               results['structure']['element_count_match']
           ])

           overall = (
               visual_score * weights['visual'] +
               content_score * weights['content'] +
               structure_score * weights['structure']
           )

           return overall

       def get_recommendation(self, results):
           score = results['overall_score']

           if score > 0.95:
               return "Excellent quality - ready for production use"
           elif score > 0.9:
               return "High quality - suitable for most use cases"
           elif score > 0.8:
               return "Good quality - minor issues may be present"
           elif score > 0.7:
               return "Acceptable quality - review recommended"
           else:
               return "Poor quality - significant issues detected"

Integration Examples
--------------------

REST API Service
~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, request, jsonify, send_file
   from pdfrebuilder.engine import DocumentEngine, BatchProcessor
   import tempfile
   import os
   import uuid
   from werkzeug.utils import secure_filename

   app = Flask(__name__)
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

   class DocumentProcessingAPI:
       def __init__(self):
           self.engine = DocumentEngine()
           self.active_jobs = {}

       def process_document(self, file_data, options=None):
           job_id = str(uuid.uuid4())

           try:
               # Save uploaded file
               with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                   tmp_input.write(file_data)
                   tmp_input.flush()

                   # Process document
                   layout = self.engine.extract(tmp_input.name)

                   # Apply options if provided
                   if options:
                       layout = self.apply_processing_options(layout, options)

                   # Generate output
                   with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                       self.engine.rebuild(layout, tmp_output.name)

                       # Store job result
                       self.active_jobs[job_id] = {
                           'status': 'completed',
                           'output_path': tmp_output.name,
                           'input_path': tmp_input.name
                       }

                       return job_id

           except Exception as e:
               self.active_jobs[job_id] = {
                   'status': 'failed',
                   'error': str(e)
               }
               return job_id

       def apply_processing_options(self, layout, options):
           # Apply custom processing options
           if options.get('use_template_mode'):
               # Enable template mode processing
               pass

           if options.get('enhance_text'):
               # Apply text enhancement
               pass

           return layout

   api = DocumentProcessingAPI()

   @app.route('/process', methods=['POST'])
   def process_document():
       if 'file' not in request.files:
           return jsonify({'error': 'No file provided'}), 400

       file = request.files['file']
       if file.filename == '':
           return jsonify({'error': 'No file selected'}), 400

       if not file.filename.lower().endswith('.pdf'):
           return jsonify({'error': 'Only PDF files are supported'}), 400

       # Get processing options
       options = request.form.get('options')
       if options:
           import json
           options = json.loads(options)

       # Process document
       job_id = api.process_document(file.read(), options)

       return jsonify({
           'job_id': job_id,
           'status': 'processing'
       })

   @app.route('/status/<job_id>')
   def get_job_status(job_id):
       if job_id not in api.active_jobs:
           return jsonify({'error': 'Job not found'}), 404

       job = api.active_jobs[job_id]
       return jsonify({
           'job_id': job_id,
           'status': job['status'],
           'error': job.get('error')
       })

   @app.route('/download/<job_id>')
   def download_result(job_id):
       if job_id not in api.active_jobs:
           return jsonify({'error': 'Job not found'}), 404

       job = api.active_jobs[job_id]
       if job['status'] != 'completed':
           return jsonify({'error': 'Job not completed'}), 400

       return send_file(
           job['output_path'],
           as_attachment=True,
           download_name='processed_document.pdf'
       )

   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=5000)

Microservice Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import aiohttp
   from aiohttp import web
   import aiofiles
   from pdfrebuilder.engine import DocumentEngine
   import json
   import tempfile
   import os

   class AsyncDocumentProcessor:
       def __init__(self):
           self.engine = DocumentEngine()
           self.processing_queue = asyncio.Queue()
           self.results_cache = {}

       async def start_workers(self, num_workers=4):
           workers = []
           for i in range(num_workers):
               worker = asyncio.create_task(self.worker(f"worker-{i}"))
               workers.append(worker)
           return workers

       async def worker(self, name):
           while True:
               try:
                   job = await self.processing_queue.get()
                   print(f"{name} processing job {job['id']}")

                   result = await self.process_job(job)
                   self.results_cache[job['id']] = result

                   self.processing_queue.task_done()

               except Exception as e:
                   print(f"Worker {name} error: {e}")

       async def process_job(self, job):
           # Simulate async processing
           await asyncio.sleep(0.1)  # Yield control

           try:
               layout = self.engine.extract(job['input_path'])
               self.engine.rebuild(layout, job['output_path'])

               return {
                   'status': 'completed',
                   'output_path': job['output_path']
               }

           except Exception as e:
               return {
                   'status': 'failed',
                   'error': str(e)
               }

       async def submit_job(self, job_data):
           await self.processing_queue.put(job_data)
           return job_data['id']

   # Create processor instance
   processor = AsyncDocumentProcessor()

   async def handle_upload(request):
       reader = await request.multipart()

       field = await reader.next()
       if field.name != 'file':
           return web.json_response({'error': 'No file field'}, status=400)

       # Save uploaded file
       with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
           async for chunk in field:
               tmp_file.write(chunk)

           job_id = f"job-{asyncio.get_event_loop().time()}"
           output_path = f"/tmp/output-{job_id}.pdf"

           job_data = {
               'id': job_id,
               'input_path': tmp_file.name,
               'output_path': output_path
           }

           await processor.submit_job(job_data)

           return web.json_response({
               'job_id': job_id,
               'status': 'queued'
           })

   async def handle_status(request):
       job_id = request.match_info['job_id']

       if job_id in processor.results_cache:
           result = processor.results_cache[job_id]
           return web.json_response({
               'job_id': job_id,
               'status': result['status'],
               'error': result.get('error')
           })
       else:
           return web.json_response({
               'job_id': job_id,
               'status': 'processing'
           })

   async def init_app():
       app = web.Application()
       app.router.add_post('/upload', handle_upload)
       app.router.add_get('/status/{job_id}', handle_status)

       # Start worker tasks
       await processor.start_workers(4)

       return app

   if __name__ == '__main__':
       web.run_app(init_app(), host='0.0.0.0', port=8080)
