# -*- coding: utf-8 -*-

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.pdftypes import PDFStream, PDFObjRef

from pdfminer.utils import isnumber

import os
import sys

def get_obj_type(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return 'dict'
    if isinstance(obj, list):
        return 'list'
    if isinstance(obj, str):
        return 'str'
    if isinstance(obj, PDFStream):
        return 'PDFStream'
    if isinstance(obj, PDFObjRef):
        return 'PDFObjRef'
    if isinstance(obj, PSKeyword):
        return 'PSKeyword'
    if isinstance(obj, PSLiteral):
        return 'PSLiteral'
    if isnumber(obj):
        return 'number'
    return 'TypeError'

def print_all_obj(filename):
    with file(filename, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser, None)
        visited_objids = set()
        for xref in doc.xrefs:
            for objid in xref.get_objids():
                if objid in visited_objids:
                    continue
                visited_objids.add(objid)
                print objid, get_obj_type(doc.getobj(objid))


def collect_image_obj(doc):
    results = []
    visited_objids = set()
    for xref in doc.xrefs:
        for objid in xref.get_objids():
            if objid in visited_objids:
                continue
            visited_objids.add(objid)
            obj = doc.getobj(objid)
            if isinstance(obj, PDFStream):
                subtype = obj.attrs.get('Subtype', None)
                if subtype is not None and subtype.name == 'Image':
                    results.append(obj)
    return results

def dump_all(filename):
    output_dir = filename + '.dumps'
    os.mkdir(output_dir)

    with file(filename, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser, None)
        image_objs = collect_image_obj(doc)
        output_count = 0
        for image_obj in image_objs:
            output_name = r'{:04d}.jpg'.format(output_count)
            output_path = os.path.join(output_dir, output_name)
            with open(output_path, 'wb') as wf:
                wf.write(image_obj.rawdata)
            output_count += 1
        print 'extract {0} images to {1}'.format(output_count, output_dir)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print 'usage: extimgpdf.py <pdf_file>'
        exit(1)
    dump_all(sys.argv[1])
