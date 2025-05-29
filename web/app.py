#!/usr/bin/env python3
import os
import sys
import json
import threading
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transcribe import transcribe_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whispertron-web-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=300, ping_interval=30)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store active transcription jobs
active_jobs = {}

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'mp4', 'mov', 'ogg', 'opus'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class WebWorker:
    """Worker class for web transcription jobs"""
    
    def __init__(self, job_id, file_path, model, language, formats, use_coreml):
        self.job_id = job_id
        self.file_path = file_path
        self.model = model
        self.language = language
        self.formats = formats
        self.use_coreml = use_coreml
        self.status = 'pending'
        self.result = None
        self.error = None
    
    def run(self):
        try:
            self.status = 'running'
            active_jobs[self.job_id] = self
            
            socketio.emit('transcription_progress', {
                'job_id': self.job_id,
                'status': 'running',
                'message': f'Starting transcription of {os.path.basename(self.file_path)}'
            })
            
            # Send periodic updates during transcription
            socketio.emit('transcription_progress', {
                'job_id': self.job_id,
                'status': 'running',
                'message': 'Transcribing audio... this may take a few minutes'
            })
            
            result = transcribe_file(
                self.file_path,
                model=self.model,
                language=self.language,
                output_formats=self.formats,
                use_coreml=self.use_coreml
            )
            
            if result and result.get('outputs'):
                self.status = 'completed'
                self.result = result
                
                socketio.emit('transcription_progress', {
                    'job_id': self.job_id,
                    'status': 'completed',
                    'message': 'Transcription completed successfully!',
                    'result': result
                })
                
                print(f"Transcription completed for job {self.job_id}:")
                for fmt, path in result['outputs'].items():
                    print(f"  {fmt}: {path}")
            else:
                self.status = 'failed'
                self.error = 'Transcription failed - no output files generated'
                
                socketio.emit('transcription_progress', {
                    'job_id': self.job_id,
                    'status': 'failed',
                    'message': 'Transcription failed - no output files generated'
                })
                
        except Exception as e:
            self.status = 'failed'
            self.error = str(e)
            
            print(f"Error in transcription job {self.job_id}: {str(e)}")
            socketio.emit('transcription_progress', {
                'job_id': self.job_id,
                'status': 'failed',
                'message': f'Error during transcription: {str(e)}'
            })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    file.save(file_path)
    
    # Get transcription settings
    model = request.form.get('model', 'tiny.en')
    language = request.form.get('language', None)
    if language == 'auto':
        language = None
    
    formats = request.form.getlist('formats')
    if not formats:
        formats = ['txt']
    
    use_coreml = request.form.get('use_coreml') == 'true'
    
    # Start transcription job
    worker = WebWorker(job_id, file_path, model, language, formats, use_coreml)
    thread = threading.Thread(target=worker.run)
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'filename': filename,
        'status': 'started'
    })

@app.route('/job/<job_id>/status')
def job_status(job_id):
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    response = {
        'job_id': job_id,
        'status': job.status
    }
    
    if job.status == 'completed' and job.result:
        response['result'] = job.result
    elif job.status == 'failed' and job.error:
        response['error'] = job.error
    
    return jsonify(response)

@app.route('/download/<job_id>/<format>')
def download_file(job_id, format):
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    if job.status != 'completed' or not job.result:
        return jsonify({'error': 'Transcription not completed'}), 400
    
    if format not in job.result['outputs']:
        return jsonify({'error': 'Format not available'}), 404
    
    file_path = job.result['outputs'][format]
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
