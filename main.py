import frida
import os
import hashlib
import argparse
import logging
import subprocess


def run_decrypt(input_dir, output_dir, convert_to_mp3=False, mp3_bitrate="320k"):
    def convert_to_mp3_file(input_file, output_file, bitrate):
        try:
            subprocess.run(
                ["ffmpeg", "-i", input_file, "-b:a", bitrate, "-y", output_file],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg conversion failed: {e.stderr}")
            return False
        except FileNotFoundError:
            logging.error("FFmpeg not found. Please install FFmpeg and add it to PATH.")
            return False
    if not os.path.exists(input_dir):
        logging.error(f"Input directory: {input_dir} does not exist.")
        return

    # get abs path
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    # hook
    session = frida.attach("QQMusic.exe")

    # load script
    script = session.create_script(open("hook_qq_music.js", "r", encoding="utf-8").read())
    script.load()

    if not os.path.exists(output_dir):
        logging.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    # for each file
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.splitext(file)
            
            # only mflac and mgg
            if file_path[-1] in [".mflac", ".mgg"]:
                logging.info(f"Decrypting {file}")
                
                # rename
                file_path = list(file_path)
                file_path[-1] = file_path[-1].replace("mflac", "flac").replace("mgg", "ogg")
                
                # check if file exists
                output_file_path = os.path.join(output_dir, "".join(file_path))
                if os.path.exists(output_file_path):
                    logging.info(f"File {output_file_path} exists, skipping...")
                    continue

                tmp_file_path = hashlib.md5(file.encode()).hexdigest()
                tmp_file_path = os.path.join(output_dir, tmp_file_path)
                tmp_file_path = os.path.abspath(tmp_file_path)
                
                # invoke script
                data = script.exports_sync.decrypt(os.path.join(root, file), tmp_file_path)
                
                # write data to file
                with open(tmp_file_path, 'wb') as f:
                    f.write(data)
                
                # rename
                os.rename(tmp_file_path, output_file_path)
                logging.info(f"Decrypt success: {output_file_path}")
                
                # Convert to MP3 if requested
                if convert_to_mp3:
                    mp3_file_path = os.path.splitext(output_file_path)[0] + ".mp3"
                    if not os.path.exists(mp3_file_path):
                        logging.info(f"Converting to MP3: {mp3_file_path}")
                        if convert_to_mp3_file(output_file_path, mp3_file_path, mp3_bitrate):
                            logging.info(f"MP3 conversion success: {mp3_file_path}")
                    else:
                        logging.info(f"MP3 file {mp3_file_path} exists, skipping...")
            elif file_path[-1] == ".lrc":
                # 处理lrc歌词文件
                lrc_file_path = os.path.join(root, file)
                output_lrc_path = os.path.join(output_dir, file)
                if not os.path.exists(output_lrc_path):
                    import shutil
                    shutil.copy2(lrc_file_path, output_lrc_path)
                    logging.info(f"Copying lyric file: {output_lrc_path}")
                else:
                    logging.info(f"Lyric file {output_lrc_path} exists, skipping...")

    session.detach()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Please input input directory")
    parser.add_argument("-o", "--output", type=str, required=True, help="Please input output directory")
    parser.add_argument("--mp3", action="store_true", help="Convert output files to MP3 format (requires FFmpeg)")
    parser.add_argument("--bitrate", type=str, default="320k", help="MP3 bitrate (e.g., 128k, 192k, 256k, 320k). Default: 320k")
    args = parser.parse_args()
    run_decrypt(args.input, args.output, args.mp3, args.bitrate)