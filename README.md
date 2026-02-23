## Music Conversion

Just batch decrypt the vip songs downloaded by QQMusic.
You should have vip privilege to download songs.

Simplified version of [decrypt-mflac-frida](https://github.com/yllhwa/decrypt-mflac-frida)

Supports:
- Platform: Windows10/11
- App version: Latest QQMusic (2025.04.12)
- Format Conversion:
  - .mflac → .flac (无损音频格式)
  - .mgg → .ogg (有损音频格式)
 
## Usage
1. Launch QQMusic and download the music
2. run the following command
    ```bash
    pip install -r requirements.txt
    python main.py -i <input_dir> -o <output_dir>
    ```

### MP3 Conversion (Optional)
To convert the output files to MP3 format, add the `--mp3` flag. You also need to have FFmpeg installed on your system and added to your PATH.

```bash
python main.py -i <input_dir> -o <output_dir> --mp3
```

You can specify the MP3 bitrate using the `--bitrate` option:

```bash
python main.py -i <input_dir> -o <output_dir> --mp3 --bitrate 320k
```

Supported bitrate options: 128k, 192k, 256k, 320k (default: 320k)

### Installing FFmpeg
- **Windows**: Download FFmpeg from https://ffmpeg.org/download.html and add it to your PATH
- **Note**: Both FLAC/OGG and MP3 files will be saved when using `--mp3` option

## Warning
This tool is only for educational purposes and is not intended for commercial use.
