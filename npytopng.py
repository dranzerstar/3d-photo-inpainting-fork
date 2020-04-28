import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.misc

output_directory = os.path.dirname('name.npy')  # 提取文件的路径
output_name = os.path.splitext(os.path.basename("name.npy"))[0]  # 提取文件名
arr = np.load('~/name.npy')  # 提取 npy 文件中的数?
disp_to_img = scipy.misc.imresize( arr , [375, 1242])  # 根据 需要的尺寸?行修改
plt.imsave(os.path.join(output_directory, "{}_disp.png".format(output_name)), arr, cmap='gray'

)



