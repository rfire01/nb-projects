
import sys,os
if "." not in sys.path:
    sys.path.append(".")
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'nbsite.settings'
import django
django.setup()
from base import annotations
import re


def process_file(id_source):
    from pyPdf import PdfFileReader
    from numpy import array
    S = {}
    locations, comments  = annotations.getPublicCommentsByFile(id_source)

    srcfile   = "tmp/%s.pdf" % (id_source)

    pdf       = PdfFileReader(file(srcfile, "rb"))
    if pdf.isEncrypted and pdf.decrypt("")==0:
        print "PDF file encrypted with non-empty password: %s" % (srcfile,)
        return False
    trim_box  = pdf.pages[0].trimBox # Sacha's coordinate system now uses this box
    crop_box  = pdf.pages[0].cropBox  # ConTeXt's page inclusion uses this box
    fudge     = (int(trim_box[2])-int(trim_box[0]))/612.0 # for the assumption of 612bp width
    bp_per_pixel = 72.0/150 * fudge

    roots       = {}
    children_of = {}
    comments_res ={}
    page_comment = {}

    for k in comments:
        node = int(k)
        parent = comments[k]['id_parent']
        if parent:
            if parent not in children_of:
                children_of[parent] = []
            children_of[parent].append(node)
        else:
            loc_id      = comments[node]['ID_location']
            loc         = locations[loc_id]
            if loc['page'] != 0:
                loc['center_x'] = loc['left'] + loc['w']/2.0
                loc['center_y'] = loc['top']  + loc['h']/2.0
            else:
                loc['center_x'] = None
                loc['center_y'] = None
            roots[node] = loc

    def oneline(s):
        return s.replace('\n', ' ')

    def texify(s):
        s = s.strip()
        patterns = [(r'\\', r'\\\\'),
                    (r'%', r'\%'), (r'\$', r'\$'), ('_', r'\_'), (r'\&', r'\&'),
                    (r'\^', r'\^\\null{}'), (r'#', r'\#'), (r'\|', r'$|$')]
        for p in patterns:
            s = re.sub(p[0], p[1], s)
        return s

    def rect2array(rect):
        return array(rect.lowerLeft+rect.upperRight, dtype=float)

    def rectangle_height(rect):
        return rect.upperRight[1]-rect.lowerLeft[1]

    S["last_page"] = -1
    def print_child(n, levels=0):
        loc_id   = comments[n]['ID_location']
        location = locations[loc_id]
        page     = int(location['page'])
        if levels == 0 and page > S["last_page"]:
            S["last_page"] = page
        if levels == 0 and page != 0:  # a root comment not on page 0 needs callout
            root = roots[n]
            # Sacha's coords are from top left corner, relative to TrimBox
            # but in pixels (not postscript points).
            # evaluate comment_box_px, with this coord system, as [llx lly wwc h]
            comment_box_px = array([root['left'],
                                    root['top']+root['h'],
                                    root['w'],
                                    root['h']])
            comment_box_bp = comment_box_px * bp_per_pixel
            # convert y coordinate to use bottom edge of trim_box as y=0
            comment_box_bp[1] = int(rectangle_height(trim_box))-int(comment_box_bp[1])
            # convert to coordinates relative to CropBox
            comment_box_bp[0:2] += (rect2array(trim_box)-rect2array(crop_box))[0:2]

            comments_res[n] = {}
            comments_res[n]['location_ID'] = loc_id
            comments_res[n]['source_ID'] = id_source
            comments_res[n]['ensemble_ID'] = locations[loc_id]['id_ensemble']
            comments_res[n]['x'] = comment_box_bp[0]
            comments_res[n]['y'] = comment_box_bp[1]
            comments_res[n]['w'] = comment_box_bp[2]
            comments_res[n]['h'] = comment_box_bp[3]
            comments_res[n]['page'] = page
            comments_res[n]['parent'] = -1

            strPage = str(page)
            if strPage in page_comment:
                tmp = page_comment[strPage]
                tmp.append(n)
                page_comment[strPage] = tmp
            else:
                page_comment[strPage] = [n]

        elif levels != 0 and page != 0:
            parent = comments[n]['id_parent']
            comments_res[n] = {}
            comments_res[n]['location_ID'] = loc_id
            comments_res[n]['source_ID'] = id_source
            comments_res[n]['ensemble_ID'] = locations[loc_id]['id_ensemble']
            comments_res[n]['x'] = comments_res[parent]['x']
            comments_res[n]['y'] = comments_res[parent]['y']
            comments_res[n]['w'] = comments_res[parent]['w']
            comments_res[n]['h'] = comments_res[parent]['h']
            comments_res[n]['page'] = page
            comments_res[n]['parent'] = parent

            strPage = str(page)
            if strPage in page_comment:
                tmp = page_comment[strPage]
                tmp.append(n)
                page_comment[strPage] = tmp
            else:
                page_comment[strPage] = [n]

        if n in children_of:
            for k in sorted(children_of[n]):
                print_child(k, levels+1)

    def cmp(a,b):
        if roots[a]['page'] == 0 and roots[b]['page'] == 0:
            return a-b              # order by comment id
        for key in ['page', 'center_y', 'center_x']:
            if roots[a][key] != roots[b][key]:
                return int(1e6*roots[a][key] - 1e6*roots[b][key])
        return 0

    for root_id in sorted(roots, cmp):
        print_child(root_id, 0)
    return comments_res , page_comment