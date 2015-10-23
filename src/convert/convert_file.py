#!/usr/bin/env python

import os
import zipfile
import shutil

from book import Book
from convert import BookConvert


class ConvertFile():
    def __init__(self):
        pass

    @staticmethod
    def convert(output_mgr, file_path, out_dir, device, verbose):
        kindle_dir = 'images' if device == 'Kindle 5' else 'Pictures'
        list_dir = []
        is_dir = os.path.isdir(file_path)

        if is_dir:
            title = os.path.basename(file_path)
            list_dir = os.listdir(file_path)
        else:
            list_dir.append(file_path)
            title = kindle_dir

        output_book = Book()
        output_book.device = device

        if title is None or title == "":
            title = kindle_dir

        files = []
        directories = []
        compressed_files = []

        # Recursively loop through the filesystem
        for filename in list_dir:
            if is_dir:
                filename = os.path.join(file_path, filename)
            if verbose:
                print("Pre-Processing %s." % filename)
            if os.path.isdir(str(filename)):
                directories.append(filename)
            else:
                if output_book.is_image_file(filename):
                    if verbose:
                        print("ConvertPkg: Found Image %s" % filename)
                    files.append(filename)
                else:
                    image_exts = ['.cbz', '.zip']

                    if os.path.splitext(filename)[1].lower() in image_exts:
                        compressed_files.append(filename)

        if len(files) > 0:
            files.sort()
            output_book.add_image_files(files)
            output_book.title = title
            book_convert = BookConvert(output_book, output_mgr, os.path.abspath(out_dir), verbose)
            book_convert.export()

        out_dir = os.path.join(out_dir, title)

        for directory in directories:
            if verbose:
                print("Converting %s", directory)
            ConvertFile.convert(output_mgr, directory, out_dir, device, verbose)

        for compressed_file in compressed_files:
            try:
                if verbose:
                    print("Uncompressing %s" % compressed_file)
                z = zipfile.ZipFile(compressed_file, 'r')
            except:
                if verbose:
                    print("Failed to convert %s. Check if it is a valid zipFile." % compressed_file)
                continue

            if is_dir:
                temp_dir = os.path.join(file_path, os.path.splitext(os.path.basename(compressed_file))[0])
            else:
                temp_dir = os.path.splitext(compressed_file)[0]

            try:
                os.mkdir(temp_dir)
            except:
                continue

            for name in z.namelist():
                temp_name = os.path.join(temp_dir, name)
                ConvertFile.extract_from_zip(name, temp_name, z)
            z.close()
            ConvertFile.convert(output_mgr, temp_dir, out_dir, device, verbose)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @staticmethod
    def extract_from_zip(name, dest_path, zip_file):
        dest_file = open(dest_path, 'wb')
        dest_file.write(zip_file.read(name))
        dest_file.close()
