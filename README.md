
<img src='imgs/horse2zebra.gif' align="right" width=384>

<br><br><br>

# CycleGAN and pix2pix in PyTorch


### Apply a pre-trained model (CycleGAN)
- You can download a pretrained model (e.g. style_vangogh) with the following script:
```bash
bash ./scripts/download_cyclegan_model.sh style_ukiyoe
bash ./scripts/download_cyclegan_model.sh style_vangogh
```
- The pretrained model is saved at `./checkpoints/{name}_pretrained/latest_net_G.pth`. Check [here](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/scripts/download_cyclegan_model.sh#L3) for all the available CycleGAN models.
- Register an account on `https://deepai.org/` and acquire your api token, then
```bash
mkdir secrets && cd secrets
vim api_key.yaml

```
- Insert `token: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` into `api_key.yaml` where `xxx...xxx` is your acquired token

- Now, go back to the ROOT directory of the repo. To test the model, you also need a folder with images
```bash
mkdir datasets/vangogh2photo && mkdir datasets/vangogh2photo/testB
```


- Then copy your images to `datasets/vangogh2photo/testB` and generate the results, which will be saved at `./results/hires`
```bash
python test.py --dataroot datasets/vangogh2photo/testB --name style_ukiyoe_pretrained --model test --no_dropout --preprocess none --display_winsize 640
python test.py --dataroot datasets/vangogh2photo/testB --name style_vangogh_pretrained --model test --no_dropout --preprocess none --display_winsize 640

```

## Acknowledgments
Our code is inspired by [pytorch-DCGAN](https://github.com/pytorch/examples/tree/master/dcgan).
