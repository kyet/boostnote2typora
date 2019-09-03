#!python3
# credit: https://github.com/silverben10/Boostnote-to-Markdown

import time
import os
import json
import cson
import re
from shutil import copyfile
from pathlib import Path
from pathvalidate import sanitize_filename
from pathvalidate import sanitize_filepath

def parse_time(time_str):
    i_date = time_str[:10]
    i_time = time_str[11:23]

    i_date = list(map(int, i_date.split("-")))
    i_time = list(map(float, i_time.split(":")))

    # time.mktime used to convert human-readable time to epoch time that can be used to update file's utime.
    t = (i_date[0], i_date[1], i_date[2], int(i_time[0]), int(i_time[1]), int(round(i_time[2], 0)), 0, 0, -1)
    output_time = time.mktime(t)

    return output_time


def set_mtime(file_path, modifiedAt):
    os.utime(file_path, (modifiedAt, modifiedAt))


def parse_folders(path):
    config_file = os.path.join(path, "boostnote.json")

    with open(config_file, "r") as f:
        config = json.load(f)

    folders = config["folders"]
    f_dict = {}

    for i in folders:
        f_dict[i["key"]] = sanitize_filepath(i["name"])

    return f_dict


def parse_image(content, title, images_path, attachment_path, asset_path):
    img_map = {}
    is_img = False

    # ex: ![ESP8266-Complete-Circuit.png](\\:storage\\0.64zrpzov2gr.png)
    r1 = re.findall(r"!\[(.*?)\]\(\\:storage\\(.*?)\)", content)
    if r1:
        is_img = True
        Path(asset_path).mkdir(exist_ok=True)
        for img in r1:
            inpath = os.path.join(images_path, img[1])
            outpath = os.path.join(asset_path, sanitize_filename(img[0]))
            #print("{} -> {}".format(inpath, outpath))
            copyfile(inpath, outpath)
            img_map["\\:storage\\" + img[1]] = "({}.assets/{})".format(title, img[0])

    # ex: ![logo_2.png](:storage\\07af9957-ada7-4f41-9558-5cb53c34982c\\4f53b514.png)
    r2 = re.findall(r"!\[(.*?)\]\(:storage\\(.*?)\)", content)
    if r2:
        is_img = True
        Path(asset_path).mkdir(exist_ok=True)
        for img in r2:
            inpath = os.path.join(attachment_path, img[1].replace("\\\\", "\\"))
            outpath = os.path.join(asset_path, sanitize_filename(img[0]))
            #print("{} -> {}".format(inpath, outpath))
            copyfile(inpath, outpath)
            img_map[":storage\\" + img[1]] = "({}.assets/{})".format(title, img[0])

    # replace content
    if is_img:
        return re.sub(r"\(((?:\\)?:storage\\.*?)\)", lambda m: img_map[m.group(1)], content)

    return content


def parse_uml(content, title):
    c = content
    # Flowchart (``` flowchart) -> (``` flow)
    (c, n) = re.subn(r"\n``` *flowchart", "\n``` flow", c)
    if n >= 1:
        print("INFO: found flowchart in [{}] and its converted".format(title))

    # LaTeX ($$$ ~ $$$) -> ($$ ~ $$)
    (c, n) = re.subn(r"\n\$\$\$", "\n$$", c)
    if n >= 1:
        print("INFO: found inline math in [{}] and its converted".format(title))

    # Inline Math ($\begin .. $\end)
    if re.search(r"\$\\begin", content):
        print("WARNING: [{}] have inline math. You have to convert manually".format(title))

    # plantuml (@startuml .. @enduml)
    if re.search(r"\n@startuml", content):
        print("WARNING: [{}] have startuml. You have to convert manually".format(title))

    return c


def parse_note(f_dict, note, note_path, attachment_path, images_path, outpath):
    # Set all the required nattributes' about the file.
    #print(note["title"])
    title = sanitize_filename(note["title"])
    #print(title)
    # Empty notes return a KeyError, since there is no content
    # Set content to empty string in this case, so they can still be exported correctly.
    try:
        content = note["content"]
    except KeyError:
        print("content not found: " + title)
        content = ""

    modified_time = parse_time(note["updatedAt"])
    folder = f_dict[note["folder"]]

    # Create the respective folder for the note to be placed in.
    output_dir = os.path.join(note_path, outpath, folder)

    try:
        # os.makedirs will (try to) create the entire folder structure from left to right, not just the rightmost file.
        os.makedirs(output_dir)
    except FileExistsError:
        # Directory already made, so continue.
        pass

    file_path = os.path.join(output_dir, title + ".md")
    asset_path = os.path.join(output_dir, title + ".assets")
    content2 = parse_image(content, title, images_path, attachment_path, asset_path)
    content3 = parse_uml(content2, title)

    # Open a new Markdown file in its respective folder, and write the contents of the .cson file to it.
    with open(file_path, "w", encoding="UTF-8") as output:
        output.write(content3)

    set_mtime(file_path, modified_time)


def parse_snippet(f_dict, note, note_path, outpath):
    title = sanitize_filename(note["title"])
    try:
        snippets = note["snippets"]
    except KeyError:
        print("snippets not found: " + title)
        snippets = ""

    # merge snippets to a single content
    # [
    #   { name: "..", mode: "text", content: '''...''' },
    #   { name: "..", mode: "text", content: '''...''' }
    # ]
    content = ""
    for s in snippets:
        content += "{}\n``` {}\n{}\n```\n".format(s["name"], s["mode"], s["content"])
    #print(content)

    modified_time = parse_time(note["updatedAt"])
    folder = f_dict[note["folder"]]

    # Create the respective folder for the note to be placed in.
    output_dir = os.path.join(note_path, outpath, folder)

    try:
        # os.makedirs will (try to) create the entire folder structure from left to right, not just the rightmost file.
        os.makedirs(output_dir)
    except FileExistsError:
        # Directory already made, so continue.
        pass

    file_path = os.path.join(output_dir, title + ".md")

    # Open a new Markdown file in its respective folder, and write the contents of the .cson file to it.
    with open(file_path, "w", encoding="UTF-8") as output:
        output.write(content)

    set_mtime(file_path, modified_time)


def main():
    # boostnote_path = "./"
    boostnote_path = "C:\\Users\\kyet\\Downloads\\boostnote-mobile\\"
    #boostnote_path = "C:\\Users\\kyet\\Downloads\\boostnote\\"
    note_path = boostnote_path + "notes"
    attachment_path = boostnote_path + "attachments"
    images_path = boostnote_path + "images"

    typora_path = os.path.join(boostnote_path, "typora")

    f_dict = parse_folders(boostnote_path)
    #print(f_dict)

    file_list = os.listdir(note_path)
    #print(file_list)

    for filename in file_list:
        with open(os.path.join(note_path, filename), "r", encoding="UTF-8") as f:
            note = cson.load(f)

        if note["isTrashed"] == "true":
            continue # skip it
        if note["type"] == "MARKDOWN_NOTE":
            parse_note(f_dict, note, note_path, attachment_path, images_path, typora_path)
        else: # snippet
            parse_snippet(f_dict, note, note_path, typora_path)


if __name__ == "__main__":
    main()