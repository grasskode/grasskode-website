#!/usr/bin/python
import argparse
import sys, os
import re

def format_post(filename, img_store):
    # check if file exists
    if os.path.exists(filename) and os.path.isfile(filename):
        print('{0} : Validated file exists.'.format(filename))
    else:
        print('{0} : File not found!'.format(filename))
        sys.exit(1)

    file = open(filename, 'r')
    filetext = file.read()
    file.close()

    # initialize formatted text to the original file text
    formattedtext = filetext

    print("\nsearching for images...\n")

    ## format the regex for images
    regex_overall = '(img=[^\n]*)'
    regex_single = '(\w+)=([^|]+)'
    for img_decl in re.findall(regex_overall, filetext):
        # a possible group of images
        images = []
        title = None
        classes = set(["postimg"])
        print('++')
        for match in re.finditer(regex_single, img_decl):
            key = match.group(1)
            if key == "href":
                images = [
                    img_store + "/" + x.strip()
                    for x in match.group(2).split(",")
                ]
            elif key == "em":
                title = match.group(2)
            elif key=="img":
                classes.update([x.strip() for x in match.group(2).split(",")])
        replacement_text = ""
        print(classes, images, title)
        if len(images) > 1:
            ## grid
            col1 = ""
            col2 = ""
            it = iter(images)
            for im in it:
                col1 += """
      <a href="{0}" data-toggle="lightbox">
        <img loading="lazy" data-src="{0}">
      </a>""".format(im)
                col2 += """
      <a href="{0}" data-toggle="lightbox">
        <img loading="lazy" data-src="{0}">
      </a>""".format(next(it))
            replacement_text = """<div class="{3}">
  <div class="grid">
    <div class="grid-column-50">{0}
    </div>
    <div class="grid-column-50">{1}
    </div>  </div>
  {2}
</div>
""".format(col1, col2, "<em>%s</em>"%title if title is not None else "", " ".join(classes))
        else:
            replacement_text = """<div class="{1}">
  <a href="{0}" data-toggle="lightbox">
    <img loading="lazy" data-src="{0}">
  </a>
  {2}
</div>
""".format(images[0], " ".join(classes), "<em>%s</em>"%title if title is not None else "")

        # search original match and replace with replacement text
        formattedtext = formattedtext.replace(img_decl, replacement_text)

    print("\nsearching for videos...\n")

    ## format the regex for videos
    regex_vimeo = '^(<iframe src="([\S]*)" width="([\S]*)" height="([\S]*)" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>)(?:\s([\S ]+))?\s'
    for match in re.finditer(regex_vimeo, filetext, re.MULTILINE):
        # a video match
        print('++')
        print('{0} - {1}x{2}'.format(match.group(2), match.group(3), match.group(4)))
        title = match.group(5)
        print(title)
        replacement_text = """<div class="postimg{1}">
    <div class="video-container">
        {0}
    </div>
    {2}
</div>
""".format(match.group(1), "" if int(match.group(3)) > int(match.group(4)) else " vertimg", "<em>%s</em>"%title if title is not None else "")

        # search original match and replace with replacement text
        formattedtext = formattedtext.replace(match.group(0), replacement_text)

    # write formattedtext to the file
    formattedfile = open('{0}'.format(filename), 'w')
    formattedfile.write(formattedtext)
    formattedfile.close()

    # all done
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('img_store')

if __name__ == '__main__':
    args = parser.parse_args()
    format_post(args.file, args.img_store)
