#!/bin/bash
pip uninstall opencv
rm -rf /usr/local/lib/python3.10/dist-packages/cv2
apt update
apt install libx11-6
ls /mnt
pip install clearml clearml-agent
python /mnt/pycharm/mtc-icvt/metacentrum/modules/mtc-train/train.py --dataset '0709b8c1' --datasets_dir '/mnt/datasets' --workdir '/mnt/' --project_name 'Test of MTC'
