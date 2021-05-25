import cv2
import os
import argparse
import shutil
from pip._vendor.distlib.compat import raw_input
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser("./pad_img.py")

    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input directory with imgs. No Default',
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output directory for saving images. No Default',
    )

    FLAGS, unparsed = parser.parse_known_args()

    if not os.path.exists(FLAGS.input):
        print(f'{FLAGS.input} does not exist, quitting ...')
        quit()



    if os.path.isdir(FLAGS.output):
        if os.listdir(FLAGS.output):
            answer = raw_input(f"Log Directory {FLAGS.output} is not empty. Do you want to proceed? [y/n]  ")
            if answer == 'n':
                quit()
            else:
                shutil.rmtree(FLAGS.output)
    if not os.path.isdir(FLAGS.output):
        os.makedirs(FLAGS.output)

    files = sorted(os.listdir(FLAGS.input))

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    bar = tqdm(total=len(files), desc='adding frame')

    for i in files:
        bar.update(1)
        input_path = os.path.join(FLAGS.input, i)
        img = cv2.imread(input_path)
        h, w, _ = img.shape
        s = min(h, w)
        white_border = int(s * 0.15)
        black_border = int(s * 0.04)

        img = cv2.copyMakeBorder(img, white_border, white_border, white_border, white_border,
                                 cv2.BORDER_CONSTANT, value=WHITE)

        img = cv2.copyMakeBorder(img, black_border, black_border, black_border, black_border,
                                 cv2.BORDER_CONSTANT, value=BLACK)

        cv2.imwrite(os.path.join(FLAGS.output, i), img)

    bar.close()
