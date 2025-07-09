import os,json,shutil,time
from pymediainfo import MediaInfo
import numpy as np
import logging
from QT import Processor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_first_frame_timecode(file_path):
    media_info = MediaInfo.parse(file_path)
    for track in media_info.tracks:
        if track.track_type == "Other":
            first_time = (getattr(track, 'time_code_of_first_frame', None))
            last_time = (getattr(track, 'time_code_of_last_frame', None))
            return first_time,last_time
            
def file_data_list(qtake_folder,input_folder):
    qtakelist = []
    camlist = []
    for filename in os.listdir(qtake_folder):
        file_path = os.path.join(qtake_folder,filename)        
        first_time,last_time = get_first_frame_timecode(file_path)
        qtake = {'filename': filename, 'first': first_time, 'last': last_time}
        qtakelist.append(qtake)
    
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder,filename)        
        first_time,last_time = get_first_frame_timecode(file_path)
        cam = {'filename': filename, 'first': first_time, 'last': last_time, 'mustcopy':0}
        camlist.append(cam)
    return qtakelist, camlist

def copy_mov_file(qtake_path, source_path, target_path,processor):
    qtakelist, camlist =file_data_list(qtake_path, source_path)
    processed_files = 0  # 处理的文件数
    for qtake in qtakelist:
        i = 0
        processed_files += 1
        print("qtakelist",len(qtakelist),processed_files)
        for cam in camlist:
            if cam["mustcopy"] == 0:
                if (cam["first"]<qtake["last"] and cam["last"]>qtake["first"]) or (cam["first"]<qtake["first"] and cam["last"]>qtake["last"]):
                    i = i+1
                    # print(qtake["filename"],qtake["first"],qtake["last"])
                    # print(cam["filename"],cam["first"],cam["last"])
                    # print(str(i))
                    # source = os.path.join(source_path, cam["filename"])
                    suffix = "." + cam["filename"].split(".")[1]
                    suffix = suffix.lower()
                    if i>1:
                        filename = qtake["filename"].replace(suffix,"("+str(i)+")"+suffix)
                        newfilename = filename
                    else:
                        newfilename = qtake["filename"]
                    source = os.path.join(source_path, cam["filename"])
                    target = os.path.join(target_path, newfilename)

                    print(source, target)
                    logging.info(f"{source} {target}")
                    shutil.copy2(source, target)
                    time.sleep(1)

                    print("\n")
        processor.update_progress.emit(processed_files, f"正在处理: {cam['filename']}")
    

if __name__ == "__main__":
    qtake_path = r"D:\test\QTake"
    source_path = r"D:\test\Cam"
    target_path = r"D:\test\Target"           
    processor = Processor()         
    copy_mov_file(qtake_path, source_path, target_path,processor)