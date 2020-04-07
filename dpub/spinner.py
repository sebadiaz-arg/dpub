#!/usr/bin/env python3
#
# Copyright (C) 2019 Telefónica S.A. All Rights Reserved
#

import sys
import threading
import time


class SpinnerException(Exception):
    pass


class Spinner:
    active = False
    delay = 0.1
    cursors = {
        'alt': '|/-\\',
        'default': '.oOo',
    }

    _DEFAULT_CURSOR = 'default'

    def __init__(self, delay=None, cursor=None):
        self.sentence = None
        self.spinner_generator = self.spinning_cursor(cursor)
        if delay and float(delay):
            self.delay = delay

    def spinning_cursor(self, cursor=None):
        if not cursor:
            cursor = Spinner._DEFAULT_CURSOR

        if cursor not in Spinner.cursors:
            raise SpinnerException('Could not find cursor on spinner')

        c = Spinner.cursors[cursor]
        while True:
            for char in c:
                yield char

    def spinner_task(self):
        while self.active:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        if self.active:
            return
        self.active = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        if not self.active:
            return
        self.active = False
        time.sleep(self.delay)

    def end(self):
        self.stop()
        self._clean_previous()

    def write(self, sentence):
        '''Prints to stdout. If there is a previous sentence, 
        it is moved back as much chars as the last sentence (if any)
        for not to move out of the current line'''
        self.stop()
        self._clean_previous()    
        self.sentence = sentence
        sys.stdout.write(sentence)
        sys.stdout.flush()
        self.start()

    def _clean_previous(self):
        if self.sentence:
            sys.stdout.write('\b' * len(self.sentence))
            # Due to jump start we have to cleanup one more char
            sys.stdout.write(' ' * (len(self.sentence)+1))
            sys.stdout.flush()
            sys.stdout.write('\b' * (len(self.sentence)+1))
            sys.stdout.flush()
