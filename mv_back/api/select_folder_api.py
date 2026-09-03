from flask import jsonify
from tkinter import filedialog, Tk
from multiprocessing import Process, Queue

def get_select_folder():
    queue = Queue()
    process = Process(target=run_dialog_in_process, args=(queue,))
    
    process.start()
    folder_path = queue.get()
    process.join()
    
    if folder_path:
        return jsonify({"success": True, "path": folder_path})
    else:
        return {"error": "Вибір скасовано"}, 200

def run_dialog_in_process(queue):
    root = Tk()
    root.withdraw()
    
    folder_path = filedialog.askdirectory(title="Виберіть папку для MediaVault")
    queue.put(folder_path)
    
    root.destroy()