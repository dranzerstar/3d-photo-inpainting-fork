import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.misc

output_directory = os.path.dirname('name.npy')  # ��敶���I�H�a
output_name = os.path.splitext(os.path.basename("name.npy"))[0]  # ��敶����
arr = np.load('~/name.npy')  # ��� npy �������I��?
disp_to_img = scipy.misc.imresize( arr , [375, 1242])  # ���� ���v�I�ڐ�?�s�C��
plt.imsave(os.path.join(output_directory, "{}_disp.png".format(output_name)), arr, cmap='gray'

)



