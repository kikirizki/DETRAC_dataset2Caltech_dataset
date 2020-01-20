import os
import os.path as path
import xml.etree.ElementTree as ET
import cv2
from glob import glob
import shutil

LABEL_FORMAT = "*.xml"
ROOT_PATH = "/home/robert/DETRAC"
# ----------------------------------------------
# ----------------------------------------------
LABEL_DIR = "DETRAC-Annotations-XML"
IMAGE_DIR = "Insight-MVT_Annotation"
# ------------------------------------------------
# ------------------------------------------------
LABEL_PATH = path.join(ROOT_PATH, LABEL_DIR)
LABEL_XMLS = glob(path.join(LABEL_PATH, LABEL_FORMAT))

print(IMAGE_DIR)

class_list = ['car', 'bus', 'van']


# [class] [identity] [x_center] [y_center] [width] [height]
def extract_traget_info(target, num):
    width = None
    left = None
    top = None
    height = None
    vechicle_type = None
    id = target.attrib["id"]

    for item in target:
        if item.tag == "box":
            box = item.attrib
            left = float(box["left"])
            top = float(box["top"])
            width = float(box["width"])
            height = float(box["height"])

        if item.tag == "attribute":
            attribute = item.attrib

            vechicle_type = attribute["vehicle_type"]
    if vechicle_type == 'others':
        class_idx = -1
    else:
        class_idx = class_list.index(vechicle_type)
    x_center = left + (width / 2.0)
    y_center = top + (height / 2.0)
    str_result = "{} {} {} {} {} {} {}".format(
        num, class_idx, id, x_center, y_center, width, height)
    return str_result


def translate_one_frame(frame_tag):
    """
    Translate one frame from xml to string
    :param frame_tag:
    :return:
    """
    str_label = []
    num = frame_tag.attrib["num"]
    for target_list in frame_tag:

        for target in target_list:
            target_info = extract_traget_info(target, num)
            str_label.append(target_info)
    return "\n".join(str_label)


def draw_rect(img_path, int_label):
    img_drawed = None
    lbl = int_label[0]
    num, cl, id, x_center, y_center, width, height = lbl

    num = str(num)
    filename = "img" + num.zfill(5)
    print("Reading {}".format(path.join(img_path, filename + ".jpg")))

    img_drawed = cv2.imread(path.join(img_path, filename + ".jpg"))
    img_drawed = cv2.putText(img_drawed, str(
        id), (x_center, y_center), cv2.FONT_HERSHEY_COMPLEX, 1, 255, 1)

    for label in int_label:
        num, cl, id, x_center, y_center, width, height = label
        left = int(x_center - (float(width) / 2))
        top = int(y_center - (float(height) / 2))
        right = left + width
        bottom = top + height
        img_drawed =cv2.putText(img_drawed,str(id),(left,top),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
        img_drawed = cv2.rectangle(img_drawed, (left, top), (right, bottom), 255, 1)
    return img_drawed


def translate_label(vid_name,image_path_root, int_label):
    lbl = int_label[0]
    num, cl, id, x_center, y_center, width, height = lbl
    num = str(num)
    img_filename = "img" + num.zfill(5)
    txt_filename = "img" + num.zfill(5)

    image_full_path = path.join(image_path_root, img_filename + ".jpg")
    txt_full_path = path.join("Caltech/labels_with_id", "{}_{}".format(vid_name,img_filename) + ".txt")
    img_cv = cv2.imread(image_full_path)
    img_height, img_width = img_cv.shape[0], img_cv.shape[1]
    assert (img_height < img_width)
    shutil.copy(image_full_path,"Caltech/images/{}_{}.jpg".format(vid_name,img_filename))
    txt_label_file = open(txt_full_path, 'w')
    print(int_label)
    print("Moving {}".format(image_full_path))
    str_label = []
    for label in int_label:
        # [class] [identity] [x_center] [y_center] [width] [height]

        num, cl, id, x_center, y_center, width, height = label
        width = float(width) / float(img_width)
        height = float(height) / float(img_height)
        x_center = float(x_center) / float(img_width)
        y_center = float(y_center) / float(img_height)
        line = "{} {} {} {} {} {}".format(
            0, id, x_center, y_center, width, height)
        str_label.append(line)
    str_label = "\n".join(str_label)
    txt_label_file.write(str_label)
    txt_label_file.close()
    print(str_label)


def draw(out_name, all_labels, imagepath_list):
    vidname = out_name.split("/")[-1].replace(".avi","")
    out = cv2.VideoWriter(out_name, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), 30,
                          (960, 540))
    for label in all_labels:

        label = label.split('\n')
        label_list = []
        for line in label:
            line = line.split(" ")
            line = [int(float(l)) for l in line]
            label_list.append(line)

        drawed_img = draw_rect(imagepath_list, label_list)
        out.write(drawed_img)
        translate_label(vidname,imagepath_list, label_list)
        cv2.imshow("test", drawed_img)
        if cv2.waitKey(15) == 'q':
            break


def translate(XML_PATHS, LABEL_DIR, IMAGE_DIR):
    for xml_path in XML_PATHS:
        # collecting all label in single video, the number of the frame == len(labels_in_one_videos)
        name = xml_path.split('/')[-1].replace('xml', 'avi')
        video_out ="videos/{}".format(name)
        labels_in_one_videos = []
        print("Reading {}".format(xml_path))
        img_file_path = xml_path.replace(
            LABEL_DIR, IMAGE_DIR).replace(".xml", "")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for elem in root:
            if elem.tag == "frame":
                string_frame = translate_one_frame(elem)
                labels_in_one_videos.append(string_frame)
        print("number of labels",len(labels_in_one_videos))
        print("number of images",len(os.listdir(img_file_path)))

        # assert len(labels_in_one_videos) == len(os.listdir(img_file_path))

        draw(video_out, labels_in_one_videos, img_file_path)



translate(LABEL_XMLS, LABEL_DIR, IMAGE_DIR)
