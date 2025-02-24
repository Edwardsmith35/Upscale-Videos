video_path="/content/drive/MyDrive/" #@param{type:"string"}
output_dir="content/drive/MyDrive/Upscaled_Videos/" #@param{type:"string"}
resolution = "2 x original" # @param ["FHD (1920 x 1080)", "2k (2560 x 1440)", "4k (3840 x 2160)","2 x original", "3 x original", "4 x original"] {type:"string"}
model = "RealESRGAN_x4plus_anime_6B" #@param ["RealESRGAN_x4plus" , "RealESRGAN_x4plus_anime_6B", "realesr-animevideov3"]

assert os.path.exists(video_path), "Video file does not exist"

video_capture = cv2.VideoCapture(video_path)
video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

final_width = None
final_height = None
aspect_ratio = float(video_width/video_height)

# Get output resolutions
match resolution:
  case "FHD (1920 x 1080)":
    final_width=1920
    final_height=1080
  case "2k (2560 x 1440)":
    final_width=2560
    final_height=1440
  case "4k (3840 x 2160)":
    final_width=3840
    final_height=2160
  case "2 x original":
    final_width=2*video_width
    final_height=2*video_height
  case "3 x original":
    final_width=3*video_width
    final_height=3*video_height
  case "4 x original":
    final_width=4*video_width
    final_height=4*video_height

if aspect_ratio == 1.0 and "original" not in resolution:
  final_height = final_width

if aspect_ratio < 1.0 and "original" not in resolution:
  temp = final_width
  final_width = final_height
  final_height = temp

scale_factor = max(final_width/video_width, final_height/video_height)
isEven = int(video_width * scale_factor) % 2 == 0 and int(video_height * scale_factor) % 2 == 0

# scale_factor needs to be even
while isEven == False:
  scale_factor += 0.01
  isEven = int(video_width * scale_factor) % 2 == 0 and int(video_height * scale_factor) % 2 == 0

print(f"Upscaling from {video_width}x{video_height} to {final_width}x{final_height}, scale_factor={scale_factor}")

!python inference_realesrgan_video.py -n {model} -i '{video_path}' -o '{output_dir}' --outscale {scale_factor}

video_name_with_ext = os.path.basename(video_path)
video_name = video_name_with_ext.replace(".mp4", "")
upscaled_video_path = f"{output_dir}{video_name}_out.mp4"
final_video_name = f"{video_name}_upscaled_{final_width}_{final_height}.mp4"
final_video_path = os.path.join(output_dir, final_video_name)

# Check if the upscaled video exists
if not os.path.exists(upscaled_video_path):
    print(f"Error: {upscaled_video_path} does not exist after upscaling.")
    exit(1)

# Cropping logic (if necessary)
if "original" not in resolution:
    print("Cropping to fit...")
    command = f"ffmpeg -loglevel verbose -hwaccel cuda -y -i '{upscaled_video_path}' -c:v h264_nvenc -filter:v 'crop={final_width}:{final_height}:(in_w-{final_width})/2:(in_h-{final_height})/2' -c:v libx264 -pix_fmt yuv420p '{final_video_path}'"
    subprocess.run(command, shell=True, check=True)
else:
    # If no cropping, use the upscaled path directly
    final_video_path = upscaled_video_path

# Check if final video exists
if not os.path.exists(final_video_path):
    print(f"Error: Final video file {final_video_path} does not exist.")
    exit(1)

# Copy to Google Drive
command = f"cp '{final_video_path}' '{save_directory_drive}/{final_video_name}'"
subprocess.run(command, shell=True, check=True)
print(f"Saved to drive: /{drive_folder}/{final_video_name}")
