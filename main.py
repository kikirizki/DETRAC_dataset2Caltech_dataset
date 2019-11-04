import os
import os.path as path
import xml.etree.ElementTree as ET
import cv2
from glob import glob
import shutil

LABEL_FORMAT = "*.xml"
ROOT_PATH = "../../DATASET/DETRAC"
TRAIN_LABEL_DIR = "DETRAC-Train-Annotations-XML"
TRAIN_IMAGE_DIR = "Insight-MVT_Annotation_Train"
TRAIN_LABEL_PATH = path.join(ROOT_PATH, TRAIN_LABEL_DIR)
LABEL_XMLS = glob(path.join(TRAIN_LABEL_PATH, LABEL_FORMAT))
OUTPUT_LABELS_DIR = "Caltech/labels_with_ids"
OUTPUT_IMAGES_DIR = "Caltech/images"
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
    str_result = "{} {} {} {} {} {} {}".format(num, class_idx, id, x_center, y_center, width, height)
    return str_result


def read_frame_tag(frame_tag):
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
    print("Reading {}".format(path.join(img_file_path, filename + ".jpg")))

    img_drawed = cv2.imread(path.join(img_file_path, filename + ".jpg"))
    img_drawed = cv2.putText(img_drawed, str(id), (x_center, y_center), cv2.FONT_HERSHEY_COMPLEX, 1, 255, 1)

    for label in int_label:
        num, cl, id, x_center, y_center, width, height = label
        left = int(x_center - (float(width) / 2))
        top = int(y_center - (float(height) / 2))
        right = left + width
        bottom = top + height

        img_drawed = cv2.rectangle(img_drawed, (left, top), (right, bottom), 255, 1)
    return img_drawed


def translate_label(imagepath_list, int_label):
    lbl = int_label[0]
    num, cl, id, x_center, y_center, width, height = lbl
    num = str(num)
    img_filename = "img" + num.zfill(5)
    txt_filename = "img" + num.zfill(5)
    image_full_path = path.join(img_file_path, img_filename + ".jpg")
    txt_full_path = path.join(OUTPUT_LABELS_DIR, img_filename + ".txt")
    img_cv = cv2.imread(image_full_path)
    img_height, img_width = img_cv.shape[0], img_cv.shape[1]
    assert (img_height < img_width)
    # shutil.copy(image_full_path,OUTPUT_IMAGES_DIR)
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
        line = "{} {} {} {} {} {}".format(cl,id,x_center,y_center,width,height)
        str_label.append(line)
    str_label = "\n".join(str_label)
    txt_label_file.write(str_label)
    txt_label_file.close()
    print(str_label)


def draw(all_label, imagepath_list):
    for label in all_labels:

        label = label.split('\n')
        label_list = []
        for line in label:
            line = line.split(" ")
            line = [int(float(l)) for l in line]
            label_list.append(line)

        drawed_img = draw_rect(imagepath_list, label_list)
        translate_label(imagepath_list, label_list)
        cv2.imshow("test", drawed_img)
        if cv2.waitKey() == 'q':
            break


for xml_file in LABEL_XMLS:
    if xml_file.split("/")[-1] == "MVI_20011.xml":
        all_labels = []
        print("Reading {}".format(xml_file))
        img_file_path = xml_file.replace(TRAIN_LABEL_DIR, TRAIN_IMAGE_DIR).replace(".xml", "")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for elem in root:
            if elem.tag == "frame":
                string_frame = read_frame_tag(elem)
                all_labels.append(string_frame)
        assert len(all_labels) == len(os.listdir(img_file_path))
        draw(all_labels, img_file_path)
        break
