import numpy as np
import argparse
import glob
import os
from functools import partial
import vispy
import scipy.misc as misc
from tqdm import tqdm
import yaml
import sys
from mesh import write_ply, read_ply, output_3d_photo
from utils import get_MiDaS_samples, read_MiDaS_depth, sparse_bilateral_filtering
import torch
import cv2
from skimage.transform import resize
import imageio
import copy
from networks import Inpaint_Color_Net, Inpaint_Depth_Net, Inpaint_Edge_Net
from MiDaS.run import run_depth
from MiDaS.run import run_depthf
from MiDaS.run import run_depthv
from MiDaS.monodepth_net import MonoDepthNet
import MiDaS.MiDaS_utils as MiDaS_utils
import matplotlib.pyplot as plt
from PIL import Image
import ffmpeg




parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='argument.yml',help='Configure of post processing')
parser.add_argument('--v', type=str, default='',help='video_input')

args = parser.parse_args()
v = args.v
config = yaml.load(open(args.config, 'r'))
os.makedirs(config['mesh_folder'], exist_ok=True)
os.makedirs(config['video_folder'], exist_ok=True)
os.makedirs(config['depth_folder'], exist_ok=True)
os.makedirs(config['depthframe_folder'], exist_ok=True)
os.makedirs(config['depthframesbs_folder'], exist_ok=True)
os.makedirs('sbsfmt-potrait90', exist_ok=True)
sample_list = get_MiDaS_samples(config['src_folder'], config['depth_folder'], config, config['specific'])
normal_canvas, all_canvas = None, None

if isinstance(config["gpu_ids"], int) and (config["gpu_ids"] >= 0):
    device = config["gpu_ids"]
else:
    device = "cpu"

print(v)

in_filename = v
imageg = Image.open(v)
image = img = cv2.imread(in_filename)      
width, height = (imageg.size)

out_filename="out.bmp"

out_frame= run_depthf(in_filename ,out_filename ,config['MiDaS_model_ckpt'],width,height, MonoDepthNet, MiDaS_utils, target_w=1000)

"""im = Image.fromarray(out_frame)
im.save("sbs.png")
"""


'''



for idx in tqdm(range(len(sample_list))):
    depth = None
    sample = sample_list[idx]
    print("Current Source ==> ", sample['src_pair_name'])
    mesh_fi = os.path.join(config['mesh_folder'], sample['src_pair_name'] +'.ply')
    image = imageio.imread(sample['ref_img_fi'])
    run_depth([sample['ref_img_fi']], config['src_folder'], config['depth_folder'],
              config['MiDaS_model_ckpt'], MonoDepthNet, MiDaS_utils, target_w=1000)
    ig=Image.open(config['src_folder']+'/'+sample['src_pair_name']+".jpg")
    w, h = (ig.size)

	
	

    arr = np.load( config['depth_folder']+'/'+sample['src_pair_name']+'.npy')
    config['output_h'], config['output_w'] = np.load(sample['depth_fi']).shape[:2]
    print("output w h",str(w)+" "+str(h))


    frac = 900 / max(config['output_h'], config['output_w'])
    config['output_h'], config['output_w'] = int(config['output_h'] * frac), int(config['output_w'] * frac)
    config['original_h'], config['original_w'] = config['output_h'], config['output_w']

    print("output w h",str(config['output_w'])+" "+str(config['output_h']))
    print("original w h",str(config['original_w'])+" "+str(config['original_h']))

    disp_to_img =np.array(Image.fromarray(arr).resize([w, h]))
    plt.imsave(os.path.join(config['depthframe_folder'], "{}_disp.jpg".format(sample['src_pair_name'])), disp_to_img, cmap='gray')

    images = [Image.open(x) for x in ['image/'+sample['src_pair_name']+".jpg",config['depthframe_folder']+"{}_disp.png".format(sample['src_pair_name']) ]]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]


    newsize = (w,h)

    finalsize= new_im.resize( newsize);
    print("resize");
    finalsize.save(config['depthframe_folder']+'/'+sample['src_pair_name']+'.jpg')


   print("mkpotrait");
    fpotrait90= finalsize.transpose(method=Image.ROTATE_270) 
    
    fpotrait90.save('sbsfmt-potrait90/'+sample['src_pair_name']+'.jpg')
'''
'''
           
    config['output_h'], config['output_w'] = np.load(sample['depth_fi']).shape[:2]
    frac = config['longer_side_len'] / max(config['output_h'], config['output_w'])
    config['output_h'], config['output_w'] = int(config['output_h'] * frac), int(config['output_w'] * frac)
    config['original_h'], config['original_w'] = config['output_h'], config['output_w']
    if image.ndim == 2:
        image = image[..., None].repeat(3, -1)
    if np.sum(np.abs(image[..., 0] - image[..., 1])) == 0 and np.sum(np.abs(image[..., 1] - image[..., 2])) == 0:
        config['gray_image'] = True
    else:
        config['gray_image'] = False
    image = cv2.resize(image, (config['output_w'], config['output_h']), interpolation=cv2.INTER_AREA)
    depth = read_MiDaS_depth(sample['depth_fi'], 3.0, config['output_h'], config['output_w'])
    mean_loc_depth = depth[depth.shape[0]//2, depth.shape[1]//2]
    if not(config['load_ply'] is True and os.path.exists(mesh_fi)):
        vis_photos, vis_depths = sparse_bilateral_filtering(depth.copy(), image.copy(), config, num_iter=config['sparse_iter'], spdb=False)
        depth = vis_depths[-1]
        model = None
        torch.cuda.empty_cache()
        print("Start Running 3D_Photo ...")
        depth_edge_model = Inpaint_Edge_Net(init_weights=True)
        depth_edge_weight = torch.load(config['depth_edge_model_ckpt'],
                                       map_location=torch.device(device))
        depth_edge_model.load_state_dict(depth_edge_weight)
        depth_edge_model = depth_edge_model.to(device)
        depth_edge_model.eval()

        depth_feat_model = Inpaint_Depth_Net()
        depth_feat_weight = torch.load(config['depth_feat_model_ckpt'],
                                       map_location=torch.device(device))
        depth_feat_model.load_state_dict(depth_feat_weight, strict=True)
        depth_feat_model = depth_feat_model.to(device)
        depth_feat_model.eval()
        depth_feat_model = depth_feat_model.to(device)
        rgb_model = Inpaint_Color_Net()
        rgb_feat_weight = torch.load(config['rgb_feat_model_ckpt'],
                                     map_location=torch.device(device))
        rgb_model.load_state_dict(rgb_feat_weight)
        rgb_model.eval()
        rgb_model = rgb_model.to(device)
        graph = None
        
        rt_info = write_ply(image,
                            depth,
                            sample['int_mtx'],
                            mesh_fi,
                            config,
                            rgb_model,
                            depth_edge_model,
                            depth_edge_model,
                            depth_feat_model)
        if rt_info is False:
            continue
        rgb_model = None
        color_feat_model = None
        depth_edge_model = None
        depth_feat_model = None
        torch.cuda.empty_cache()
    if config['save_ply'] is True or config['load_ply'] is True:
        verts, colors, faces, Height, Width, hFov, vFov = read_ply(mesh_fi)
    else:
        verts, colors, faces, Height, Width, hFov, vFov = rt_info
    videos_poses, video_basename = copy.deepcopy(sample['tgts_poses']), sample['tgt_name']
    top = (config.get('original_h') // 2 - sample['int_mtx'][1, 2] * config['output_h'])
    left = (config.get('original_w') // 2 - sample['int_mtx'][0, 2] * config['output_w'])
    down, right = top + config['output_h'], left + config['output_w']
    border = [int(xx) for xx in [top, down, left, right]]
    normal_canvas, all_canvas = output_3d_photo(verts.copy(), colors.copy(), faces.copy(), copy.deepcopy(Height), copy.deepcopy(Width), copy.deepcopy(hFov), copy.deepcopy(vFov),
                        copy.deepcopy(sample['tgt_pose']), sample['video_postfix'], copy.deepcopy(sample['ref_pose']), copy.deepcopy(config['video_folder']),
                        image.copy(), copy.deepcopy(sample['int_mtx']), config, image,
                        videos_poses, video_basename, config.get('original_h'), config.get('original_w'), border=border, depth=depth, normal_canvas=normal_canvas, all_canvas=all_canvas,
                        mean_loc_depth=mean_loc_depth)
'''