"""
The purpose of this script is to determine the estimated (X,Y) coordinates of a robot given a single image with the
robot previously detected.

Variables are defined as the parameters from the camera which captured the given image in this example.

All position vectors are measured in meters

"""

import numpy as np


# Given the pixel location z, obtain a normalized image point estimate
def distortion_corrected(distort_co_, x_est_nor_dis_, y_est_nor_dis_, error_):
    y_normalized = y_est_nor_dis_         # estimate of normalized image point (y coordinate)
    x_normalized = x_est_nor_dis_         # estimate of normalized image point (x coordinate)

    while 1:
        rho_squared = pow(x_normalized, 2) + pow(y_normalized, 2)   # step 2 to obtain normalized image point estimate
        beta_radial = 1 + rho_squared * distort_co_[0] + pow(rho_squared, 2) * distort_co_[1] \
                      + pow(rho_squared, 4) * distort_co_[4]         # radial lens distortion parameter

        # tangential lens distortion vectors
        d_x = 2 * distort_co_[2] * x_normalized * y_normalized + distort_co_[3] \
              * (rho_squared + 2 * pow(x_normalized, 2))
        d_y = distort_co_[2] * (rho_squared + 2 * pow(y_normalized, 2)) \
              + 2 * distort_co_[3] * x_normalized * y_normalized

        x_temp = (x_est_nor_dis_ - d_x) / beta_radial
        y_temp = (y_est_nor_dis_ - d_y) / beta_radial

        if abs(x_temp - x_normalized) < error_ and abs(y_temp - y_normalized < error_):
            x_pixel_ = x_temp
            y_pixel_ = y_temp
            return x_pixel_, y_pixel_

        else:
            x_normalized = x_temp
            y_normalized = y_temp


f_u = 707  # focal distance along the U axis (I frame)
f_v = 693  # focal distance along the V axis (I frame)
h0 = 0.104  # height above the XY-plane of the T frame
ST = np.array([[0.441], [0.231], [2.219]])  # position vector of the sensor from the T-frame origin
ST_z = ST[2]  # z value of the position vector
skewCo = 0  # skew coefficient (intrinsic parameter)

center_x = 261  # (i believe) coordinates of the optical center (in pixels)
center_y = 265
S2T = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]])  # no idea what this is

distort_co = np.array([0.289, -1.08, 0.0102, -0.0244, 3.13])  # image distortion coefficient vector

x_pixel_dis = 441
y_pixel_dis = 313

# estimated normalized image points including distortion
y_est_nor_dis = (y_pixel_dis - center_y) / f_v
x_est_nor_dis = (x_pixel_dis - center_x) / (f_u - (skewCo * y_est_nor_dis))

error = 0.000001
x_pixel, y_pixel = distortion_corrected(distort_co, x_est_nor_dis, y_est_nor_dis, error)

datalength = ["image1"]

# Determine geolocation estimate for the estimated normalized image point
for image1 in datalength:
    q = np.array([[x_pixel], [y_pixel], [1]])             # estimated normalized image point
    us = q / np.linalg.norm(q)                      # estimate of the unit vector along the LOS vector u^s
    u_z = np.array([])
    u_z = np.dot(S2T, us)

    # estimated range from the S frame origin to the estimated target position on the surface of the Earth
    r = (h0 - ST_z) / u_z[2]
    ot = np.add(ST, r * u_z)      # zero-mean Gaussian inertial navigation system (INS) error

print("The estimated X value =", ot[0])
print("The estimated Y value =", ot[1])
