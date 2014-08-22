#!/usr/bin/env python

# The output_manager synchronizes the output display for all the various threads

# ####################
import threading


class OutputStruct():
    def __init__(self):
        self.id = 0
        self.updateObjSem = None
        self.title = ""
        self.numOfInc = 0


class OutputManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.output_objs = dict()
        self.output_list_lock = threading.Lock()

        # Used to assign the next id for an output object
        self.next_id = 0

        self.isAlive = True

    def create_output_obj(self, name, number_of_increments):
        raise NotImplementedError('Should have implemented this')

    def update_output_obj(self, object_id):
        raise NotImplementedError('Should have implemented this')

    def run(self):
        raise NotImplementedError('Should have implemented this')

    def stop(self):
        self.isAlive = False
