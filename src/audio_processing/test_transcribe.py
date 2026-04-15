import sys
import os
from transcriber import transcribe_audio, save_transcript_json, save_transcript_txt, save_transcript_srt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.video_processing.loader import extract_audio_from_video
from transcriber import transcribe_long_audio

# AUDIO TEST
# result = transcribe_audio( audio_path='data/raw/audio/Inception _ The Dream Sequence _ HBO Max [mpj9dL7swwk]_trailer.mp3', model_size='base', word_timestamps=True)

# print(f"Language detected : {result['language']} ", f"({result['language_probability']:.0%} confidence)")
# print(f"Duration          : {result['duration_s']}s")
# print(f"Segments          : {len(result['segments'])}")
# print(f"Full text preview : {result['full_text'][:200]}...")


# print('\n--- Segments ---')
# for seg in result['segments']:
#     print(f"  [{seg['start']:.1f}s -> {seg['end']:.1f}s] {seg['text']}")

# if result['segments'] and 'words' in result['segments'][0]:
#     print('\n--- Word Confidence (first segment) ---')
#     for w in result['segments'][0]['words']:
#         conf_label = 'HIGH' if w['probability'] >= 0.8 else (
#                      'MED'  if w['probability'] >= 0.5 else 'LOW')
#         print(f"  [{conf_label}] {w['word']:<15} {w['probability']:.2f}")

# save_transcript_json(result, 'data/processed/transcripts/sample.json')
# save_transcript_txt (result, 'data/processed/transcripts/sample.txt')
# save_transcript_srt (result, 'data/processed/transcripts/sample.srt')
# print('\nSaved: JSON, TXT, SRT')


# VIDEO TEST
# VIDEO      = 'data/raw/video/Inception _ The Dream Sequence _ HBO Max_trailer.mp4'
# AUDIO_OUT  = 'data/processed/audio/from_video.mp3'
# TRANS_OUT  = 'data/processed/transcripts/from_video.json'

# print('Step 1: Extracting audio from video...')
# audio_path = extract_audio_from_video(VIDEO, AUDIO_OUT)
# print(f'  Audio saved: {audio_path}')

# print('Step 2: Transcribing extracted audio...')
# result = transcribe_audio(audio_path, model_size='base', word_timestamps=True)

# save_transcript_json(result, TRANS_OUT)
# print(f'  Transcript saved: {TRANS_OUT}')
# print(f"  Text preview: {result['full_text'][:300]}")

# LONG AUDIO 
result = transcribe_long_audio(
    audio_path='../../data/raw/audio/Diabetes Explained in 5 Minutes. What Doctors Wont Tell You_ [Clx0oaCNErg].mp3',
    output_dir='../../data/processed/transcripts/chunks/',
    model_size='base',
    chunk_minutes=5.0
)

print(f"Total segments : {len(result['segments'])}")
print(f"Full text length: {len(result['full_text'])} characters")
print(f"Preview: {result['full_text'][:400]}")