import frida
import os
import hashlib
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import logging


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)


class MusicDecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Conversion")
        self.root.geometry("600x500")

        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        ttk.Label(main_frame, text="输出格式:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        self.format_var = tk.StringVar(value="flac_ogg")
        ttk.Radiobutton(format_frame, text="FLAC/OGG", variable=self.format_var, value="flac_ogg").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="MP3", variable=self.format_var, value="mp3").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="两者都要", variable=self.format_var, value="both").pack(side=tk.LEFT, padx=5)
        
        row += 1

        ttk.Label(main_frame, text="MP3比特率:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        self.bitrate_var = tk.StringVar(value="320k")
        bitrate_combo = ttk.Combobox(main_frame, textvariable=self.bitrate_var, state="readonly", width=10)
        bitrate_combo['values'] = ["128k", "192k", "256k", "320k"]
        bitrate_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        row += 1

        ttk.Label(main_frame, text="输入文件夹:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        self.input_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(input_frame, text="浏览...", command=self.browse_input).grid(row=0, column=1, padx=5)
        
        row += 1

        ttk.Label(main_frame, text="输出文件夹:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="浏览...", command=self.browse_output).grid(row=0, column=1, padx=5)
        
        row += 1

        self.start_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.start_button.grid(row=row, column=0, columnspan=2, pady=10)
        
        row += 1

        ttk.Label(main_frame, text="日志:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        row += 1

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.rowconfigure(row, weight=1)

    def setup_logging(self):
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)

    def convert_to_mp3_file(self, input_file, output_file, bitrate):
        try:
            subprocess.run(
                ["ffmpeg", "-i", input_file, "-b:a", bitrate, "-y", output_file],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg转换失败: {e.stderr}")
            return False
        except FileNotFoundError:
            logging.error("未找到FFmpeg。请安装FFmpeg并将其添加到PATH环境变量中。")
            return False

    def run_decrypt(self):
        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        format_choice = self.format_var.get()
        bitrate = self.bitrate_var.get()

        if not input_dir or not output_dir:
            logging.error("请选择输入和输出文件夹")
            return

        if not os.path.exists(input_dir):
            logging.error(f"输入文件夹不存在: {input_dir}")
            return

        input_dir = os.path.abspath(input_dir)
        output_dir = os.path.abspath(output_dir)

        try:
            session = frida.attach("QQMusic.exe")
        except frida.ProcessNotFoundError:
            logging.error("未找到QQMusic.exe进程，请先启动QQ音乐")
            return

        script = session.create_script(open("hook_qq_music.js", "r", encoding="utf-8").read())
        script.load()

        if not os.path.exists(output_dir):
            logging.info(f"创建输出文件夹: {output_dir}")
            os.makedirs(output_dir)

        for root, dirs, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.splitext(file)
                
                if file_path[-1] in [".mflac", ".mgg"]:
                    logging.info(f"正在解密: {file}")
                    
                    file_path = list(file_path)
                    file_path[-1] = file_path[-1].replace("mflac", "flac").replace("mgg", "ogg")
                    
                    output_file_path = os.path.join(output_dir, "".join(file_path))
                    
                    if format_choice == "mp3":
                        mp3_file_path = os.path.splitext(output_file_path)[0] + ".mp3"
                        if os.path.exists(mp3_file_path):
                            logging.info(f"MP3文件 {mp3_file_path} 已存在，跳过...")
                            continue
                    else:
                        if os.path.exists(output_file_path):
                            logging.info(f"文件 {output_file_path} 已存在，跳过...")
                            continue

                    tmp_file_path = hashlib.md5(file.encode()).hexdigest()
                    tmp_file_path = os.path.join(output_dir, tmp_file_path)
                    tmp_file_path = os.path.abspath(tmp_file_path)
                    
                    data = script.exports_sync.decrypt(os.path.join(root, file), tmp_file_path)
                    
                    with open(tmp_file_path, 'wb') as f:
                        f.write(data)
                    
                    os.rename(tmp_file_path, output_file_path)
                    logging.info(f"解密成功: {output_file_path}")
                    
                    if format_choice in ["mp3", "both"]:
                        mp3_file_path = os.path.splitext(output_file_path)[0] + ".mp3"
                        if not os.path.exists(mp3_file_path):
                            logging.info(f"正在转换为MP3: {mp3_file_path}")
                            if self.convert_to_mp3_file(output_file_path, mp3_file_path, bitrate):
                                logging.info(f"MP3转换成功: {mp3_file_path}")
                            
                            if format_choice == "mp3":
                                os.remove(output_file_path)
                        else:
                            logging.info(f"MP3文件 {mp3_file_path} 已存在，跳过...")

        session.detach()
        logging.info("所有文件处理完成！")

    def start_conversion(self):
        self.start_button.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.run_decrypt)
        thread.daemon = True
        thread.start()
        
        def check_thread():
            if thread.is_alive():
                self.root.after(100, check_thread)
            else:
                self.start_button.config(state="normal")
        
        check_thread()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    root = tk.Tk()
    app = MusicDecryptorGUI(root)
    root.mainloop()
