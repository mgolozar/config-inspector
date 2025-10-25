from __future__ import annotations


import time
from pathlib import Path
from typing import Callable, Dict

 

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):

    def on_created(self, event):
        print(event.src_path)
        return super().on_created(event)

    def on_modified(self, event):
        print(event.src_path)
        return super().on_modified(event)

    def on_delted(self, event):  
        print(event) # <DirModifiedEvent: event_type=modified, src_path='/Users/felixschuermeyer/Coding/watchDogTest', is_directory=True>
        print(event.src_path) # /Users/felixschuermeyer/Coding/watchDogTest
        print(event.is_directory) # True
        print(event.event_type)

def watch_polling(root: Path, on_change: Callable[[], None]) -> None:
 

    
    event_handler = Handler()

    observer = Observer()
    observer.schedule(event_handler, root , recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        print("Observer stopping")
    finally:
        observer.stop()
        observer.join()
    

       




 