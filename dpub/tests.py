#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

# This module reads from existing spreadsheet the defined data
# and composes the skeletom of places to write

from dpub.ref import (get_fixed_cell_part, get_movable_cell_part, split_location,
                      join_location, join_cell, next_row, next_col, opposite_dimension)
from dpub.drive import COLS_DIMENSION, ROWS_DIMENSION


class Test:
    '''The representation of an executed test and its results per profile. 
    It also includes the representation of where the results must be allocated
    in the final document'''

    def __init__(self, id, name, id_location, name_location, first_message_location, result_location=None, asserts_location=None, new=False):
        '''Creates an instance of Test'''
        self.id = id
        self.name = name
        self.id_location = id_location
        self.name_location = name_location
        self.first_message_location = first_message_location
        self.result_location = result_location
        self.asserts_location = asserts_location
        self.new = new
        self.items = []

    def append(self, item):
        '''Appends a test item. Updates the test name
        if null and item has a test name'''
        self.items.append(item)
        self._update_test_name_from_the_item_one(item)

    def success(self):
        '''Returns true if response of the test was successful
        for all the composing items'''
        for i in self.items:
            if not i.success():
                return False
        return True

    def _update_test_name_from_the_item_one(self, item):
        if not item:
            return
        if not self.name and item.test_name:
            self.name = item.test_name


class Loader:

    def __init__(self, drive, first_id_loc, first_msg_loc, first_result_loc=None, first_asserts_loc=None, major_dimension=COLS_DIMENSION):
        self._drive = drive
        # This is the dimension that remains unaltered during test loading
        self._dim = major_dimension

        _, c = split_location(first_id_loc)
        # This is the value that will be incrementing as tests are composed
        self._movable = get_movable_cell_part(c, self._dim)

        # The sheet and fixed part of the test ids location
        self._id_sheet, c = split_location(first_id_loc)
        self._id_fixed = get_fixed_cell_part(c, self._dim)

        # The sheet and fixed part of the test name location. This is taken by default
        # as the next_col/next_row of the id_sheet
        self._name_sheet = self._id_sheet
        if self._dim == COLS_DIMENSION:
            self._name_fixed = next_col(self._id_fixed)
        else:
            self._name_fixed = next_row(self._id_fixed)

        # The sheet and fixed part of the message traces location
        self._msg_sheet, c = split_location(first_msg_loc)
        self._msg_fixed = get_fixed_cell_part(c, self._dim)

        # The sheet and fixed part of the result location
        self._res_sheet = None
        self._res_fixed = None
        if first_result_loc:
            self._res_sheet, c = split_location(first_result_loc)
            self._res_fixed = get_fixed_cell_part(c, self._dim)

        # the sheet and fixed part of the assert location
        self._ass_sheet = None
        self._ass_fixed = None
        if first_asserts_loc:
            self._ass_sheet, c = split_location(first_asserts_loc)
            self._ass_fixed = get_fixed_cell_part(c, self._dim)

    def load(self, ids):
        '''From a list of test identifiers, compose the test objects.
        For every read id, the writable cells are incremented in their
        movable dimension (Depending if writing in rows or in columns)'''
        tests_map = {}
        for id in ids:
            # Skip empty ids. They belong to intermediate empty rows or columns when reading existing tests
            if len(id) > 0:
                # Read at m_loc. If m_loc content is not empty at the sheet, skip the
                # test. Only destination empty cells for messages will be written
                m_loc = self._msg_loc()
                if self._is_location_empty(m_loc):
                    tests_map[id] = Test(
                        id, None, self._id_loc(), self._name_loc(), m_loc, self._res_loc(), self._ass_loc())

            # Increment movable dimension
            self._inc()

        return tests_map

    def create(self, id, name):
        '''Creates a new test and populates the writing locations with the 
        current in cursor.Takes advantage of a previous call to load to continue increasing
        in the same direction the movable dimension, to complete the new tests.
        These new tests come from the input message traces but they are not found
        in the drive spreadsheet'''
        t = Test(id, name, self._id_loc(), self._name_loc(), self._msg_loc(),
                 self._res_loc(), self._ass_loc(), new=True)
        self._inc()
        return t

    def _is_location_empty(self, loc):
        '''Returns true if at least the content of the
        first cell of the received location is empty.'''
        dst = self._drive.read_one(loc)
        return len(dst) == 0

    def _join_cell(self, fixed):
        '''Composes the cell based on the fixed part, the movable
        and the dimesion'''
        if self._dim == ROWS_DIMENSION:
            return join_cell(self._movable, fixed)
        return join_cell(fixed, self._movable)

    def _join_location(self, sheet, fixed):
        '''Composes the location based on the fixed part, the movable
        part, the sheet and the dimension'''
        return join_location(sheet, self._join_cell(fixed))

    def _id_loc(self):
        '''Returns the current cursor test id location'''
        return self._join_location(self._id_sheet, self._id_fixed)

    def _name_loc(self):
        '''Returns the current cursor test name location'''
        return self._join_location(self._name_sheet, self._name_fixed)

    def _msg_loc(self):
        '''Returns the current cursor messages location'''
        return self._join_location(self._msg_sheet, self._msg_fixed)

    def _res_loc(self):
        '''Returns the current cursor results location. None if not requested
        results in the final spreadsheet'''
        if not self._res_fixed:
            return None
        if not self._res_sheet:
            return None
        return self._join_location(self._res_sheet, self._res_fixed)

    def _ass_loc(self):
        '''Returns the current cursor asserts location. None if not requested
        asserts in the final spreadsheet'''
        if not self._ass_fixed:
            return None
        if not self._ass_sheet:
            return None
        return self._join_location(self._ass_sheet, self._ass_fixed)

    def _inc(self):
        '''Increments the movable in one unit'''
        if self._dim == COLS_DIMENSION:
            self._movable = next_row(self._movable)
        else:
            self._movable = next_col(self._movable)
