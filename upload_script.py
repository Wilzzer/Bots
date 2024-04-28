import os
import re
import time
import schedule
import glob
import datetime
from drivobot import GoogleDrivito

RES_FOLDER = "Ressources/Temp/"

def file_upload():
    del_delay = datetime.timedelta(minutes=5)
    files = glob.glob(os.path.join("./"+RES_FOLDER, "*.jpg"))
    print(files)
    for file in files:
        folder_id = None
        filename = os.path.basename(file)
        filedir = os.path.dirname(file)
        img_ctime = datetime.datetime.fromtimestamp(os.path.getctime(file))
        indexes = [x.start() for x in re.finditer('!', filename)]
        
        if(indexes):
            folder_id = filename[indexes[0]+1:indexes[1]]
            old_name = filename
            try:
                new_name = filedir+"/"+filename[len(folder_id)+2:]
                os.rename(file, new_name)
                drive.upload_file(new_name, folder_id)
                os.remove(new_name)
            except:
                print("Couldn't upload file :", old_name)
                os.rename(file, old_name)
        if(img_ctime+del_delay<datetime.datetime.now()):
            os.remove(file)
    return 

def main():
    global drive
    drive = GoogleDrivito()

    schedule.every(5).seconds.do(file_upload)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
