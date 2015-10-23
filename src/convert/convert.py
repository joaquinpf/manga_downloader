#!/usr/bin/env python

# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import imghdr

import image


class BookConvert():
    def __init__(self, book, output_mgr, directory, verbose):
        self.book = book
        self.outputMgr = output_mgr
        self.directory = directory
        self.verbose = verbose

    def export(self):

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        if not self.verbose:
            output_idx = self.outputMgr.create_output_obj("Converting " + self.book.title, len(self.book.images))

        for index in range(0, len(self.book.images)):
            directory = os.path.join(unicode(self.directory), unicode(self.book.title))
            source = unicode(self.book.images[index])
            new_source = os.path.join(self.book.images[index] + "." + imghdr.what(str(source)))
            target = os.path.join(directory, '%05d.png' % index)
            if self.verbose:
                print(str(index) + " Target = " + target)

            if index == 0:
                try:
                    if not os.path.isdir(directory):
                        os.makedirs(directory)

                except OSError:
                    return

                try:
                    base = os.path.join(directory, unicode(self.book.title))
                    manga_name = base + '.manga'
                    if self.verbose:
                        print(manga_name)
                    if self.book.overwrite or not os.path.isfile(manga_name):
                        manga = open(manga_name, 'w')
                        manga.write('\x00')
                        manga.close()

                    manga_save_name = base + '.manga_save'
                    if self.book.overwrite or not os.path.isfile(manga_save_name):
                        manga_save = open(base + '.manga_save', 'w')
                        save_data = u'LAST=/mnt/us/pictures/%s/%s' % (self.book.title, os.path.split(target)[1])
                        if self.verbose:
                            print("SaveData = " + save_data)
                        manga_save.write(save_data.encode('utf-8'))
                        manga_save.close()

                except IOError:
                    return False

            os.renames(source, new_source)

            try:
                if self.book.overwrite or not os.path.isfile(target):
                    image.convert_image(new_source, target, str(self.book.device), self.book.imageFlags)
                    if self.verbose:
                        print(source + " -> " + target)
                    else:
                        self.outputMgr.update_output_obj(output_idx)
            except RuntimeError:
                print("ERROR")
            finally:
                os.renames(new_source, source)

