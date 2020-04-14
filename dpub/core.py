#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import os
import re

from dpub import cli, drive, output, parser, pipe
from dpub.ref import (extend_cell_location_to_range, join_location, next_cell,
                      next_cell_range, opposite_dimension, prepare_id_range,
                      split_location)
from dpub.spinner import Spinner
from dpub.tests import Loader


class DPubError(Exception):
    pass


def run(dimension=drive.COLS_DIMENSION):
    '''Parses the input read from stdin and publishes it to
    the drive spreadsheet'''
    spinner = Spinner()
    spinner.write('Reading from stdin ... ')

    # Parse cli input parameters
    args = cli.parse_args()
    doc = args.spreadsheet
    creds = args.credentials
    token = args.token
    first_id_location = args.first_test_location
    first_msg_location = args.first_msg_location
    first_result_location = args.result
    first_asserts_location = args.asserts
    mode = args.mode

    spinner.write('Setup Google Drive access ... ')
    d = drive.Drive(doc, creds, token)
    loader = Loader(d,
                    first_id_location,
                    first_msg_location,
                    first_result_location,
                    first_asserts_location,
                    dimension)

    ids_range = extend_cell_location_to_range(first_id_location, dimension)
    ids = d.read(ids_range, dimension)

    spinner.write('Reading existing tests ... ')
    tests_map = loader.load(ids)
    spinner.write('Read existing tests completed. ')

    new_tests_map = {}

    # Complete tests with the parsed items
    items = _compose_items()
    for it in items:
        id = it.test_id
        if id not in ids:
            # Not recognized id in the spreadsheet is added in a map as well
            # as its related name (both got from traces item) to compose new tests
            # to be appended at the end of the spreadsheet
            if id not in new_tests_map:
                spinner.write('Found new test {} ... '.format(id))
                new_tests_map[id] = loader.create(id, it.test_name)
            new_tests_map[id].append(it)
            continue

        if id not in tests_map:
            # If test is not in map is because it exists but is not writable. Skip
            continue

        spinner.write('Preparing test {} ... '.format(id))
        t = tests_map[id]
        t.append(it)

    # Join both old and new tests in a single map before writing
    tests_map.update(new_tests_map)

    # Write them to drive
    spinner.write('Writing results to spreadsheet ... ')
    for _, t in tests_map.items():
        # Skip tests empty on items, because they can be headers of other not valid spreadsheet lines taken as tests
        if len(t.items) == 0:
            continue

        spinner.write('Writting test {} ... '.format(t.id))

        if t.new:
            d.write_one(t.id_location, t.id)
            if t.name:
                d.write_one(t.name_location, t.name)

        msg_values = output.compose_msgs(t, mode)
        d.write(t.first_message_location, msg_values,
                opposite_dimension(dimension))

        if t.result_location:
            res = output.compose_result(t)
            d.write_one(t.result_location, res)

        if t.asserts_location:
            asserts = output.compose_asserts_string(t)
            d.write_one(t.asserts_location, asserts)

    spinner.write('Done.')
    spinner.end()


def _compose_items():
    '''Reads input queue and composes the items map. Every item
    is a trace to write for a test'''
    items = []
    q = pipe.to_queue()
    while not q.empty():
        it = parser.parse_item(q)
        # Skip null items, as they are related with completion
        # lines at the end not belonging to any test
        if it:
            items.append(it)
    return items
