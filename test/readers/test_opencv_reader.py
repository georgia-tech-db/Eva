# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest

import cv2
import numpy as np

from src.readers.opencv_reader import OpenCVReader
from test.util import custom_list_of_dicts_equal

NUM_FRAMES = 10


class VideoLoaderTest(unittest.TestCase):

    def create_dummy_frames(self, num_frames=NUM_FRAMES,
                            filters=[], start_id=0):
        if not filters:
            filters = range(num_frames)
        for idx, i in enumerate(filters):
            yield {'id': start_id + idx,
                   'data': np.array(
                       np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                       dtype=np.uint8)}

    def create_sample_video(self):
        try:
            os.remove('dummy.avi')
        except FileNotFoundError:
            pass

        out = cv2.VideoWriter('dummy.avi',
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (2, 2))
        for i in range(NUM_FRAMES):
            frame = np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                             dtype=np.uint8)
            out.write(frame)

    def setUp(self):
        self.create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_loader = OpenCVReader(file_url='dummy.avi')
        batches = list(video_loader.read())
        expected = list(self.create_dummy_frames())
        self.assertEqual(len(batches), NUM_FRAMES)
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        print(actual)
        print(expected)
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_return_batches_equivalent_to_number_of_frames_2(self):
        video_loader = OpenCVReader(file_url='dummy.avi', batch_size=-1)
        batches = list(video_loader.read())
        expected = list(self.create_dummy_frames())
        self.assertEqual(len(batches), NUM_FRAMES)
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_loader = OpenCVReader(file_url='dummy.avi', offset=2)
        batches = list(video_loader.read())
        expected = list(
            self.create_dummy_frames(
                filters=[i for i in range(2, NUM_FRAMES)]))

        self.assertEqual(NUM_FRAMES - 2, len(batches))
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_return_single_batch_if_batch_size_equal_to_no_of_frames(
            self):
        video_loader = OpenCVReader(
            file_url='dummy.avi', batch_size=NUM_FRAMES)
        batches = list(video_loader.read())
        expected = list(
            self.create_dummy_frames(filters=[i for i in range(NUM_FRAMES)]))
        self.assertEqual(1, len(batches))
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_skip_first_two_frames_and_batch_size_equal_to_no_of_frames(
            self):
        video_loader = OpenCVReader(
            file_url='dummy.avi', batch_size=NUM_FRAMES, offset=2)
        batches = list(video_loader.read())
        expected = list(self.create_dummy_frames(
            filters=[i for i in range(2, NUM_FRAMES)]))
        self.assertEqual(1, len(batches))
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_start_frame_number_from_two(self):
        video_loader = OpenCVReader(
            file_url='dummy.avi', batch_size=NUM_FRAMES, start_frame_id=2)
        batches = list(video_loader.read())
        expected = list(self.create_dummy_frames(
            filters=[i for i in range(0, NUM_FRAMES)], start_id=2))
        self.assertEqual(1, len(batches))
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))

    def test_should_start_frame_number_from_two_and_offset_from_one(self):
        video_loader = OpenCVReader(
            file_url='dummy.avi',
            batch_size=NUM_FRAMES,
            offset=1,
            start_frame_id=2)
        batches = list(video_loader.read())
        expected = list(self.create_dummy_frames(
            filters=[i for i in range(1, NUM_FRAMES)], start_id=2))
        self.assertEqual(1, len(batches))
        actual = [batch.frames.to_dict('records')[0] for batch in batches]
        self.assertTrue(custom_list_of_dicts_equal(actual, expected))
