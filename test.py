"""General-purpose test script for image-to-image translation.

Once you have trained your model with train.py, you can use this script to test the model.
It will load a saved model from '--checkpoints_dir' and save the results to '--results_dir'.

It first creates model and dataset given the option. It will hard-code some parameters.
It then runs inference for '--num_test' images and save results to an HTML file.

Example (You need to train models first or download pre-trained models from our website):
    Test a CycleGAN model (both sides):
        python test.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan

    Test a CycleGAN model (one side only):
        python test.py --dataroot datasets/vangogh2photo/testB --name style_vangogh_pretrained --model test --no_dropout

    The option '--model test' is used for generating CycleGAN results only for one side.
    This option will automatically set '--dataset_mode single', which only loads the images from one set.
    On the contrary, using '--model cycle_gan' requires loading and generating results in both directions,
    which is sometimes unnecessary. The results will be saved at ./results/.
    Use '--results_dir <directory_path_to_save_result>' to specify the results directory.

    Test a pix2pix model:
        python test.py --dataroot ./datasets/facades --name facades_pix2pix --model pix2pix --direction BtoA

See options/base_options.py and options/test_options.py for more test options.
See training and test tips at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/tips.md
See frequently asked questions at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/qa.md
"""
import os
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util.visualizer import save_images
from util import html
import cv2
from tqdm import tqdm
import requests
import urllib.request
import numpy as np
import yaml


if __name__ == '__main__':
    opt = TestOptions().parse()  # get test options
    # hard-code some parameters for test
    opt.num_threads = 0   # test code only supports num_threads = 0
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    # create a website
    web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  # define the website directory
    if opt.load_iter > 0:  # load_iter is 0 by default
        web_dir = '{:s}_iter{:d}'.format(web_dir, opt.load_iter)
    print('creating web directory', web_dir)
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))
    # test with eval mode. This only affects layers like batchnorm and dropout.
    # For [pix2pix]: we use batchnorm and dropout in the original pix2pix. You can experiment it with and without eval() mode.
    # For [CycleGAN]: It should not affect CycleGAN as CycleGAN uses instancenorm without dropout.
    if opt.eval:
        model.eval()
    bar = tqdm(total=len(dataset))
    for i, data in enumerate(dataset):

        # if i >= opt.num_test:  # only apply our model to opt.num_test images.
        #     break
        model.set_input(data)  # unpack data from data loader
        model.test()           # run inference
        visuals = model.get_current_visuals()  # get image results
        img_path = model.get_image_paths()     # get image paths
        # if i % 5 == 0:  # save images to an HTML file
        #     print('processing (%04d)-th image... %s' % (i, img_path))
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
        bar.update(1)
        bar.set_description(f'processing {img_path}')
    bar.close()
    webpage.save()  # save the HTML

    results_folder = f'./results/{opt.name}/test_latest/images'
    # results_folder = f'./results/style_ukiyoe_pretrained/test_latest/images'
    original_folder = './datasets/vangogh2photo/testB'
    hires_folder = './results/hires'
    lr_imgs = [i for i in sorted(os.listdir(results_folder)) if i.endswith('_fake.png')]
    original_imgs = sorted(os.listdir(original_folder))
    if not os.path.isdir(hires_folder):
        os.mkdir(hires_folder)

    bar = tqdm(total=len(lr_imgs), desc='low-res -> hi-res')
    # v1
    # for i in lr_imgs:
    #     bar.update(1)
    #     img_name = i[:-9]
    #     original_img_path = [i for i in original_imgs if os.path.splitext(i)[0] == img_name]
    #     if len(original_img_path) == 0:
    #         print(f'Cannot find image {img_name} from the original folder...')
    #         continue
    #     img_ori = cv2.imread(os.path.join(original_folder, original_img_path[0]))
    #     o_h, o_w, _ = img_ori.shape
    #
    #     img_cur = cv2.imread(os.path.join(results_folder, i))
    #     # img_cur = cv2.resize(img_cur, (o_w, o_h), cv2.INTER_AREA)
    #     # img_cur = cv2.resize(img_cur, (o_w, o_h), cv2.INTER_CUBIC)
    #     img_cur = cv2.resize(img_cur, (o_w*2, o_h*2), cv2.INTER_LINEAR)
    #     cv2.imwrite(os.path.join(hires_folder, img_name + '.png'), img_cur)

    #v2
    secret = yaml.safe_load(open('secrets/api_key.yaml', 'r'))
    for i in lr_imgs:
        bar.update(1)
        img_name = i[:-9]
        try:
            r = requests.post(
                "https://api.deepai.org/api/torch-srgan",
                files={
                    'image': open(os.path.join(results_folder, i), 'rb'),
                },
                headers={'api-key': secret['token']}
            )

            with urllib.request.urlopen(r.json()['output_url']) as url:
                arr = np.asarray(bytearray(url.read()), dtype=np.uint8)

            hires_img = cv2.imdecode(arr, -1)
            cv2.imwrite(os.path.join(hires_folder, img_name + '.png'), hires_img)
        except Exception as e:
            print('Failed', e)

    bar.close()

