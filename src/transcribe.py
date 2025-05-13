#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
import multiprocessing
import shutil
from datetime import datetime

def get_optimal_threads():
    """Get optimal number of threads for M4 Max"""
    cpu_count = multiprocessing.cpu_count()
    
    # M4 Max typically has 14-16 CPU cores
    if cpu_count >= 16:
        # Leave a few cores free for system processes
        return cpu_count - 2
    elif cpu_count >= 8:
        return cpu_count - 1
    else:
        return max(4, cpu_count)

def transcribe_file(file_path, model="large-v3", language=None, task="transcribe", 
                   output_formats=["txt", "srt", "vtt"], use_coreml=True):
    """
    Transcribe an audio file using whisper.cpp
    """
    # Ensure file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    # Get base filename without extension
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("exports", f"{name_without_ext}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process m4a files - convert to wav first since whisper.cpp may not handle m4a well
    input_file = file_path
    temp_wav_path = None
    
    if file_ext == '.m4a':
        print(f"Converting m4a file to wav format for compatibility")
        temp_wav_path = os.path.join(output_dir, f"{name_without_ext}.wav")
        ffmpeg_cmd = [
            "ffmpeg", "-i", file_path, 
            "-ar", "16000", # 16kHz sample rate
            "-ac", "1",     # mono audio
            "-c:a", "pcm_s16le", # 16-bit PCM
            temp_wav_path
        ]
        
        try:
            print(f"Running FFmpeg conversion: {' '.join(ffmpeg_cmd)}")
            ffmpeg_process = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if ffmpeg_process.returncode != 0:
                print(f"Error converting audio: {ffmpeg_process.stderr}")
                return None
                
            input_file = temp_wav_path
            print(f"Successfully converted to {temp_wav_path}")
        except Exception as e:
            print(f"Failed to convert m4a: {e}")
            return None
    
    # Create the full output file base path (without extension)
    output_file_base = os.path.join(output_dir, name_without_ext)
    
    # Use absolute paths to avoid any directory navigation issues
    abs_output_file_base = os.path.abspath(output_file_base)
    abs_file_path = os.path.abspath(input_file)
    
    # Build command
    cmd = [os.path.abspath("bin/whisper")]
    
    # Add model
    model_path = os.path.abspath(f"models/whisper_models/ggml-{model}.bin")
    cmd.extend(["-m", model_path])
    
    # Add input file
    cmd.extend(["-f", abs_file_path])
    
    # Add language if specified
    if language:
        cmd.extend(["-l", language])
    
    # Add output formats
    for fmt in output_formats:
        cmd.append(f"-o{fmt}")
        
    # Set output file path (without extension)
    cmd.extend(["-of", abs_output_file_base])
    
    # Add CoreML optimization if requested
    if use_coreml:
        coreml_model = os.path.abspath(f"models/whisper_models/ggml-{model}-coreml.mlmodelc")
        if os.path.exists(coreml_model):
            cmd.extend(["--coreml", coreml_model])
    
    # Add basic quality parameters
    cmd.extend([
        "--beam-size", "5",
        "--best-of", "5", 
        "--temperature", "0.0",
        "--max-len", "60",
        f"--threads", str(get_optimal_threads())
    ])
    
    # Execute command
    print(f"Running transcription with command: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print(f"Error during transcription: {process.stderr}")
        return None
    
    # Check console output
    print(f"STDOUT: {process.stdout}")
    print(f"STDERR: {process.stderr}")
    
    # Return info about the transcription
    results = {
        "original_file": file_path,
        "output_dir": output_dir,
        "outputs": {}
    }
    
    # Check for output files - they should be in the format "{output_file_base}.{fmt}"
    for fmt in output_formats:
        expected_file = f"{abs_output_file_base}.{fmt}"
        
        if os.path.exists(expected_file):
            print(f"Found output file: {expected_file}")
            results["outputs"][fmt] = expected_file
        else:
            print(f"Looking for file: {expected_file}")
            # Sometimes whisper.cpp creates files in unexpected locations
            # Let's check a few possibilities:
            
            # 1. Without the full path
            local_file = f"{name_without_ext}.{fmt}"
            if os.path.exists(local_file):
                target_file = os.path.join(output_dir, f"{name_without_ext}.{fmt}")
                shutil.copy(local_file, target_file)
                print(f"Found file in current directory, copied to: {target_file}")
                results["outputs"][fmt] = target_file
                
                # Clean up the file in the current directory
                os.remove(local_file)
            else:
                # 2. Try with just the output directory
                alternate_file = f"{output_dir}.{fmt}"
                if os.path.exists(alternate_file):
                    target_file = os.path.join(output_dir, f"{name_without_ext}.{fmt}")
                    shutil.move(alternate_file, target_file)
                    print(f"Found file with alternate name, moved to: {target_file}")
                    results["outputs"][fmt] = target_file
                else:
                    print(f"Could not find output file for format {fmt}")
    
    # Print debug info
    print(f"Output directory: {output_dir}")
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        print(f"Files in output directory: {files}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper")
    parser.add_argument("file", help="Audio file to transcribe")
    parser.add_argument("--model", default="large-v3", help="Model to use (tiny.en, base.en, small.en, medium.en, large-v3)")
    parser.add_argument("--language", help="Language code (en, fr, etc.)")
    parser.add_argument("--formats", default="txt,srt,vtt", help="Output formats (comma-separated)")
    parser.add_argument("--no-coreml", action="store_true", help="Disable CoreML acceleration")
    
    args = parser.parse_args()
    
    formats = args.formats.split(",")
    result = transcribe_file(
        args.file, 
        model=args.model,
        language=args.language,
        output_formats=formats,
        use_coreml=not args.no_coreml
    )
    
    if result:
        print(f"Transcription complete!")
        for fmt, path in result["outputs"].items():
            print(f"- {fmt.upper()}: {path}")

if __name__ == "__main__":
    main() 