

## EXPERIMENTAL ##
# This script extracts active parts from an audio file based on short-term energy.
# It aims to only use the "active" parts of the audio for further processing.

import os
import librosa
import numpy as np
import soundfile as sf

def extract_active_parts(audio_file, output_dir, threshold=0.1, min_duration=1.0, segment_duration=5.0):
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Compute the short-term energy
    energy = librosa.feature.rms(y=y)

    # Apply thresholding to find active parts
    active_frames = np.where(energy > threshold * np.max(energy))[1]

    # Convert active frames to time
    active_times = librosa.frames_to_time(active_frames, sr=sr)

    # Merge adjacent active segments
    active_segments = []
    if active_times.size > 0:
        current_segment_start = active_times[0]
        for t in active_times[1:]:
            if len(active_segments) > 0 and t - active_segments[-1][1] <= min_duration:
                active_segments[-1] = (current_segment_start, t)
            else:
                active_segments.append((current_segment_start, t))
                current_segment_start = t

    # Extract and save 5-second segments
    for i, segment in enumerate(active_segments):
        start_time, end_time = segment
        while end_time - start_time >= segment_duration:
            segment_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(audio_file))[0]}_{i}.wav")
            segment_audio = y[int(start_time*sr):int((start_time + segment_duration)*sr)]
            sf.write(segment_file, segment_audio, sr)
            start_time += segment_duration

# Example usage
audio_file = 'california dreamin.wav'
output_dir = 'output_segments'
os.makedirs(output_dir, exist_ok=True)
extract_active_parts(audio_file, output_dir)
