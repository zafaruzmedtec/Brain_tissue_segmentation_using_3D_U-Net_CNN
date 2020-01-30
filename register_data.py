# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 01:37:06 2018

@author: ZT
"""
# True performs the registration or inverse transform, False - not
Register_all_data = False
Inverse_transform_predict_test = False
Inverse_transform_predict_valid = False

import numpy as np
import os
from os import listdir
from PIL import Image as PImage
from shutil import copyfile
import shutil
from shutil import move

folder_name = './'
data_path = 'Data_Original/'
test_folder = 'Test_Set/'
train_folder = 'Training_Set/'
valid_folder = 'Validation_Set/'
transform_folder = 'transformations/'
register_folder = 'registered/'
images_out_folder = 'images/'
segment_out_folder = 'segment/'
elastix_folder = 'bin/'
param_folder = 'parameters/'
rigid_file = 'rigid.txt'
bspline_file = 'nonrigid.txt' # Metric "AdvancedMattesMutualInformation"
bspline_file_inv = 'nonrigid_inv_trans.txt' # modified Metric to "DisplacementMagnitudePenalty"
ext = '.nii'
img_for_reg_folder = 'img_for_reg/'
seg_for_reg_folder = 'seg_for_reg/'
test_reg_folder = 'test/'
test_trans_folder = 'test_reg2orig_trans_param/'
valid_trans_folder = 'valid_reg2orig_trans_param/'

# create folders
if not os.path.exists(folder_name + data_path + img_for_reg_folder): # temporary img_for_reg folder in data folder
    os.makedirs(folder_name + data_path + img_for_reg_folder)
if not os.path.exists(folder_name + data_path + seg_for_reg_folder): # temporary seg_for_reg folder in data folder
    os.makedirs(folder_name + data_path + seg_for_reg_folder)
if not os.path.exists(folder_name + transform_folder + test_trans_folder): # test_reg2orig_trans_param in transformation folder
    os.makedirs(folder_name + transform_folder + test_trans_folder)
if not os.path.exists(folder_name + register_folder): # registered folder
    os.makedirs(folder_name + register_folder)
if not os.path.exists(folder_name + register_folder + test_reg_folder): # test folder in registered folder
    os.makedirs(folder_name + register_folder + test_reg_folder)
if not os.path.exists(folder_name + register_folder + images_out_folder): # images folder in registered folder
    os.makedirs(folder_name + register_folder + images_out_folder)
if not os.path.exists(folder_name + register_folder + segment_out_folder): # segment folder in registered folder
    os.makedirs(folder_name + register_folder + segment_out_folder)
if not os.path.exists(folder_name + register_folder + valid_trans_folder): # valid folder in registered folder
    os.makedirs(folder_name + register_folder + valid_trans_folder)

# function split and copy src images to img or seg folder data set
def copy_images(src, dst, seg_dst):
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if file_name.endswith("seg.nii"):
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, seg_dst)
        else:
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dst)

# copy temporarly data set to img_for_reg and seg_for_reg folder, in order to load and read easily
copy_images(folder_name + data_path + train_folder, folder_name + data_path + img_for_reg_folder, folder_name + data_path + seg_for_reg_folder) #copy train set
copy_images(folder_name + data_path + valid_folder, folder_name + data_path + img_for_reg_folder, folder_name + data_path + seg_for_reg_folder) #copy valid set
#copy_images(folder_name + data_path + test_folder, folder_name + data_path + img_for_reg_folder, folder_name + data_path + seg_for_reg_folder) #copy test set

# function returns array of images from path folder
def loadImages(path):
    imagesList = listdir(path)
    loadedImages = []
    for image in imagesList:
        if image.endswith(ext):
            loadedImages.append(image)
    return loadedImages

test_images = loadImages(folder_name + data_path + test_folder) # load test images
int_images = loadImages(folder_name + data_path + img_for_reg_folder) # load train and valid images
int_images = int_images + test_images # concatenate train, test and valid images
seg_images = loadImages(folder_name + data_path + seg_for_reg_folder) # load seg images


if Register_all_data:
    for i in range(0,len(int_images)):
        print("Image: ", i)
        
        f_name = os.path.basename(int_images[5]) #5 - fixed IBSR_07.nii image
        m_name = os.path.basename(int_images[i])
    
        if i in range(0,len(seg_images)):
            m_seg_name = os.path.basename(seg_images[i])
        else:
            m_seg_name = 'None'
        
        if not os.path.exists(folder_name + transform_folder + m_name):
            os.makedirs(folder_name + transform_folder + m_name)
        if not os.path.exists(folder_name + transform_folder + test_trans_folder + m_name):
            os.makedirs(folder_name + transform_folder + test_trans_folder + m_name)
        
        # Register the train, validation and test set on IBSR_07.nii image with inverse transform
        
        str1 = 'elastix'                                                              # for linux (folder_name + elastix_folder + 'elastix')
        str1 = str1 + ' -f ' + folder_name + data_path + img_for_reg_folder + f_name  # get fixed image
        if m_name in test_images:
            str1 = str1 + ' -m ' + folder_name + data_path + test_folder + m_name     # get moving image from test folder
        else:
            str1 = str1 + ' -m ' + folder_name + data_path + img_for_reg_folder + m_name  # get moving image from img_for_reg_folder
        str1 = str1 + ' -out ' + folder_name + transform_folder + m_name + '/'        # get output folder
        str1 = str1 + ' -p ' + folder_name + param_folder + bspline_file              # get non-rigid parameter file
        status = os.system(str1)
        
        # replace (ResultImageFormat "mhd" with "nii"
        with open(folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
            filedata1 = file1.read()
        filedata1 = filedata1.replace('mhd', 'nii')
        with open(folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
            file1.write(filedata1)
        
        # Non-rigid inverse transform of image:
        str2 = 'transformix'                                                              # for linux (folder_name + elastix_folder + 'transformix')
        if m_name in test_images:
            str2 = str2 + ' -in ' + folder_name + data_path + test_folder + m_name        # image to transform
        else:
            str2 = str2 + ' -in ' + folder_name + data_path + img_for_reg_folder + m_name # image to transform
        str2 = str2 + ' -out ' + folder_name + register_folder + images_out_folder        # get output folder
        str2 = str2 + ' -tp ' + folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt' # get inverse transformation parameters
        status = os.system(str2)
        # rename result
        shutil.move(folder_name + register_folder + images_out_folder + 'result.nii', folder_name + register_folder + images_out_folder + m_name)
    
        # replace FinalBSplineInterpolationOrder 3 with 0
        with open(folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
            filedata1 = file1.read()
        filedata1 = filedata1.replace('FinalBSplineInterpolationOrder 3', 'FinalBSplineInterpolationOrder 0')
        with open(folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
            file1.write(filedata1)
    
        # Non-rigid inverse transform of segmentation:
        str2 = 'transformix'                                                               # for linux (folder_name + elastix_folder + 'transformix')
        str2 = str2 + ' -in ' + folder_name + data_path + seg_for_reg_folder + m_seg_name  # image to transform
        str2 = str2 + ' -out ' + folder_name + register_folder + segment_out_folder        # get output folder
        str2 = str2 + ' -tp ' + folder_name + transform_folder + m_name + '/' + 'TransformParameters.0.txt' # get inverse transformation parameters
        status = os.system(str2)
        # rename result
        shutil.move(folder_name + register_folder + segment_out_folder + 'result.nii', folder_name + register_folder + segment_out_folder + m_name)
    
        # Register the registered test set on original test set accordingly
        if m_name in test_images:
            str3 = 'elastix'                                                              # for linux (folder_name + elastix_folder + 'elastix')
            str3 = str3 + ' -f ' + folder_name + data_path + test_folder + m_name         # get fixed image 
            str3 = str3 + ' -m ' + folder_name + register_folder + test_reg_folder + m_name  # get moving image from test folder
            str3 = str3 + ' -out ' + folder_name + transform_folder + test_trans_folder + m_name + '/'  # get output folder
            str3 = str3 + ' -p ' + folder_name + param_folder + bspline_file              # get non-rigid parameter file
            status = os.system(str3)
    
            # replace (ResultImageFormat "mhd" with "nii"
            with open(folder_name + transform_folder + test_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
                filedata1 = file1.read()
            filedata1 = filedata1.replace('mhd', 'nii')
            with open(folder_name + transform_folder + test_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
                file1.write(filedata1)
            # replace FinalBSplineInterpolationOrder 3 with 0
            with open(folder_name + transform_folder + test_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
                filedata1 = file1.read()
            filedata1 = filedata1.replace('FinalBSplineInterpolationOrder 3', 'FinalBSplineInterpolationOrder 0')
            with open(folder_name + transform_folder + test_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
                file1.write(filedata1)
#    
#    #############
if Inverse_transform_predict_test:
    
    prediction_folder = 'prediction_final/'
    pred_test_folder = 'Test/'
    predict_test_register_folder = 'predict_test_converted_vox2orig/'
    
    predict_test_img = loadImages(folder_name + prediction_folder + pred_test_folder)
    
    for i in range(0,len(predict_test_img)): 
        print("Image: ", i)
        
        #f_name = os.path.basename(int_images[5]) #5 - fixed IBSR_07.nii image
        m_name = os.path.basename(predict_test_img[i])
        
        if not os.path.exists(folder_name + transform_folder + test_trans_folder + m_name):
            os.makedirs(folder_name + transform_folder + test_trans_folder + m_name)
        
        
        str4 = 'transformix'                                                               # for linux (folder_name + elastix_folder + 'transformix')
        str4 = str4 + ' -in ' + folder_name + prediction_folder + pred_test_folder + m_name  # image to transform
        str4 = str4 + ' -out ' + folder_name + register_folder + predict_test_register_folder        # get output folder
        str4 = str4 + ' -tp ' + folder_name + transform_folder + test_trans_folder + m_name + '/' + 'TransformParameters.0.txt' # get inverse transformation parameters
        status = os.system(str4)
        # rename result
        shutil.move(folder_name + register_folder + predict_test_register_folder + 'result.nii', folder_name + register_folder + predict_test_register_folder + m_name)
        


if Inverse_transform_predict_valid:
    
        # Register the registered validation set
    prediction_folder = 'prediction_final/'
    pred_valid_folder = 'Validation/'
    predict_valid_register_folder = 'predict_valid_converted_vox2orig/'
    predict_valid_img = loadImages(folder_name + prediction_folder + pred_valid_folder)
    
    for i in range(0,len(predict_valid_img)):
        print("Image: ", i)
        #f_name = os.path.basename(int_images[5]) #5 - fixed IBSR_07.nii image
        m_name = os.path.basename(predict_valid_img[i])
        
        if not os.path.exists(folder_name + transform_folder + valid_trans_folder + m_name):
            os.makedirs(folder_name + transform_folder + valid_trans_folder + m_name)
            
        str5 = 'elastix'                                                              # for linux (folder_name + elastix_folder + 'elastix')
        str5 = str5 + ' -f ' + folder_name + data_path + valid_folder + m_name         # get fixed image 
        str5 = str5 + ' -m ' + folder_name + register_folder + images_out_folder + m_name  # get moving image from test folder
        str5 = str5 + ' -out ' + folder_name + transform_folder + valid_trans_folder + m_name + '/'  # get output folder
        str5 = str5 + ' -p ' + folder_name + param_folder + bspline_file              # get non-rigid parameter file
        status = os.system(str5)
        
        # replace (ResultImageFormat "mhd" with "nii"
        with open(folder_name + transform_folder + valid_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
            filedata1 = file1.read()
        filedata1 = filedata1.replace('mhd', 'nii')
        with open(folder_name + transform_folder + valid_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
            file1.write(filedata1)
        # replace FinalBSplineInterpolationOrder 3 with 0
        with open(folder_name + transform_folder + valid_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'r') as file1:
            filedata1 = file1.read()
        filedata1 = filedata1.replace('FinalBSplineInterpolationOrder 3', 'FinalBSplineInterpolationOrder 0')
        with open(folder_name + transform_folder + valid_trans_folder + m_name + '/' + 'TransformParameters.0.txt', 'w') as file1:
            file1.write(filedata1)
        
        str6 = 'transformix'                                                               # for linux (folder_name + elastix_folder + 'transformix')
        str6 = str6 + ' -in ' + folder_name + prediction_folder + pred_valid_folder + m_name  # image to transform
        str6 = str6 + ' -out ' + folder_name + register_folder + predict_valid_register_folder        # get output folder
        str6 = str6 + ' -tp ' + folder_name + transform_folder + valid_trans_folder + m_name + '/' + 'TransformParameters.0.txt' # get inverse transformation parameters
        status = os.system(str6)
        # rename result
        shutil.move(folder_name + register_folder + predict_valid_register_folder + 'result.nii', folder_name + register_folder + predict_valid_register_folder + m_name)
        
    
shutil.rmtree(folder_name + data_path + img_for_reg_folder) # delete temporary img dataset
shutil.rmtree(folder_name + data_path + seg_for_reg_folder) # delete temporary seg dataset