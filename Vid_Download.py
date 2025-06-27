import subprocess
import os
from yt_dlp import YoutubeDL

# === STEP 1: Input and config ===
video_url = input("Enter the video URL: ").strip()
download_filename = "raw_download.mp4"
final_filename = "cropped_video.mp4"

ydl_opts = {
    # 'format': 'bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/best[height=1080]',
    'format': 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]',
    'merge_output_format': 'mp4',
    'outtmpl': download_filename
}

# === STEP 2: Download the video ===
print("\n🔽 Downloading video...")
with YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

# === STEP 3: Crop black bars using ffmpeg cropdetect ===
def crop_black_bars(input_file, output_file):
    print("\n✂️ Cropping black bars...")

    # Step 1: Detect crop area
    cropdetect_command = [
        'ffmpeg', '-i', input_file,
        '-vf', 'cropdetect=24:16:0',  # 24-frame check, 16-pixel round
        '-frames:v', '100',  # Check first 100 frames
        '-f', 'null', '-'
    ]

    result = subprocess.run(cropdetect_command, stderr=subprocess.PIPE, text=True)
    
    crop_lines = [line for line in result.stderr.split('\n') if 'crop=' in line]
    if not crop_lines:
        print("❌ Could not detect crop area.")
        return

    last_crop = crop_lines[-1].split('crop=')[-1]

    # Step 2: Apply crop to output
    crop_command = [
        'ffmpeg', '-i', input_file,
        '-vf', f'crop={last_crop}',
        '-c:a', 'copy',
        output_file
    ]
    subprocess.run(crop_command)
    print(f"\n✅ Cropped video saved as: {output_file}")

# === STEP 4: Execute Crop ===
if os.path.exists(download_filename):
    crop_black_bars(download_filename, final_filename)
else:
    print("❌ Video download failed, cannot crop.")
