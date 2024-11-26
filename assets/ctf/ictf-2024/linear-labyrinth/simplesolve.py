import torch
import numpy as np
import cv2
from model import Model

model = Model()
model.load_state_dict(torch.load('model.pth'))

# Read in the output image, keep in mind we saved a float32 image
flag = cv2.imread('testing_input.png', 0)

steps = list(model.children())

tensor = torch.from_numpy(flag).to(torch.float32)

for step in steps:
    tensor = step(tensor)

out_arr = tensor.detach().numpy()

cv2.imwrite('testing_output.png', out_arr)

# print('Out shape:', out.shape)

# print('Out dtype:', out.dtype)

# print('Out Contents:', out)

# z = torch.from_numpy(out).to(torch.float32) # out_arr is not equal to out 

# # reversed_steps = list(model.children())[::-1] # reverse the order of the layers
# steps = reversed(list(model.children())) # reverse the order of the layers

# for step in steps:
#     z = z - step.bias
#     z = z[..., None]
#     z = torch.linalg.pinv(step.weight) @ z
#     z = torch.squeeze(z)

# # print('Agreement between the two snippets:', torch.dist(out_tensor, z))

# # Reconstruct the image
# reconstructed_arr = z.detach().numpy() 
# # Convert all values to integers

# # Write the array to a text file containing the contents of reconstructed_arr
# np.savetxt('reconstructed_arr.txt', reconstructed_arr, fmt='%d')

# cv2.imwrite('testing2.png', reconstructed_arr)