#!/usr/bin/env python

# The progressBarManager synchronizes the progress bars for the program

# ####################

from output_manager.base import *
from output_manager.progress_bar import *
import time


class ProgressBarManager(OutputManager):
    def __init__(self):
        OutputManager.__init__(self)

    def create_output_obj(self, title, number_of_pages):
        output_obj = OutputStruct()
        output_obj.updateObjSem = threading.Semaphore(0)
        output_obj.title = title

        output_obj.numOfInc = number_of_pages

        # Aquiring the List Lock to protect the dictionary structured
        self.output_list_lock.acquire(True)

        cur_id = self.next_id
        self.next_id += 1
        output_obj.id = cur_id
        self.output_objs[cur_id] = output_obj

        #  Releasing lock
        self.output_list_lock.release()

        return cur_id

    def update_output_obj(self, object_id):
        self.release_semaphore(object_id)

    def get_next_idx(self):
        index = None

        self.output_list_lock.acquire(True)
        if len(self.output_objs) > 0:
            keys = self.output_objs.iterkeys()
            for key in keys:
                index = key
                break
        self.output_list_lock.release()

        return index

    def remove_ouput_obj(self, index):
        self.output_list_lock.acquire(True)
        del self.output_objs[index]
        self.output_list_lock.release()

    def acquire_semaphore(self, index):
        # Get a pointer to the semaphore
        # Lock the list to protect the interior map structure while
        # retrieving the pointer to the semaphore
        self.output_list_lock.acquire(True)
        sem = self.output_objs[index].updateObjSem
        self.output_list_lock.release()

        sem.acquire()

        return

    def release_semaphore(self, index):
        # Get a pointer to the semaphore
        # Lock the list to protect the interior map structure while
        # retrieving the pointer to the semaphore
        self.output_list_lock.acquire(True)
        sem = self.output_objs[index].updateObjSem
        self.output_list_lock.release()

        sem.release()

    def run(self):
        while self.isAlive:
            # Sleep to give priority to another thread
            time.sleep(0)
            index = self.get_next_idx()
            if index is not None:
                widgets = ['%s: ' % self.output_objs[index].title, Percentage(), ' ', Bar(), ' ', ETA(), ]
                progress_bar = ProgressBar(widgets=widgets, maxval=self.output_objs[index].numOfInc).start()

                for i in range(self.output_objs[index].numOfInc):
                    self.acquire_semaphore(index)
                    progress_bar.update(i + 1)
                print ("\n")
                self.remove_ouput_obj(index)




