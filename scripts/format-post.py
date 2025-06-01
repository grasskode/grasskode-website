#!/usr/bin/python
import argparse
import sys, os
import re

def format_post(filename):
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
    regex_single = '<a data-flickr-embed="true" [a-z=" -]*href=\"[\S]*\" title="[^"]*"><img src="([\S]*).jpg" width="([\S]*)" height="([\S]*)" alt="[^"]*"><\/a><script async src="[\S]*" charset="utf-8"><\/script>'
    regex_multiple = '((?:<a data-flickr-embed="true" [a-z=" -]*href=\"[\S]*\" title="[^"]*"><img src="[\S]*.jpg" width="[\S]*" height="[\S]*" alt="[^"]*"><\/a><script async src="[\S]*" charset="utf-8"><\/script>\s)+)([\S ]+\s)?\s'
    for match in re.finditer(regex_multiple, filetext):
        # a possible group of images
        num_images = 0
        images = []
        print('++')
        for match_single in re.finditer(regex_single, match.group(0)):
            # this is a single image in a possible grid
            print('{0} - {1}x{2}'.format(match_single.group(1), match_single.group(2), match_single.group(3)))
            num_images += 1
            images.append((match_single.group(1), False if int(match_single.group(2)) > int(match_single.group(3)) else True))
        title = match.group(2)
        print(title)
        replacement_text = ""
        if len(images) > 1:
            ## grid
            col1 = ""
            col2 = ""
            it = iter(images)
            for im in it:
                col1 += """      <a href="{0}_c.jpg" data-toggle="lightbox">
        <img loading="lazy" data-src="{0}.jpg">
      </a>
""".format(im[0])
                col2 += """      <a href="{0}_c.jpg" data-toggle="lightbox">
        <img loading="lazy" data-src="{0}.jpg">
      </a>
""".format(next(it)[0])
            replacement_text = """<div class="postimg">
  <div class="grid">
    <div class="grid-column-50">
{0}
    </div>
    <div class="grid-column-50">
{1}
    </div>  </div>
  {2}
</div>

""".format(col1, col2, "<em>%s</em>"%title if title is not None else "")
        else:
            replacement_text = """<div class="postimg{1}">
  <a href="{0}_c.jpg" data-toggle="lightbox">
    <img loading="lazy" data-src="{0}.jpg">
  </a>
  {2}
</div>

""".format(images[0][0], " vertimg" if images[0][1] else "", "<em>%s</em>"%title if title is not None else "")

        # search original match and replace with replacement text
        formattedtext = formattedtext.replace(match.group(0), replacement_text)

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

if __name__ == '__main__':
    args = parser.parse_args()
    format_post(args.file)
