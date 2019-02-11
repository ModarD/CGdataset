#!/usr/bin/python
# The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
#
#   This example program shows how to use dlib's implementation of the paper:
#   One Millisecond Face Alignment with an Ensemble of Regression Trees by
#   Vahid Kazemi and Josephine Sullivan, CVPR 2014
#
#   In particular, we will train a face landmarking model based on a small
#   dataset and then evaluate it.  If you want to visualize the output of the
#   trained model on some images then you can run the
#   face_landmark_detection.py example program with predictor.dat as the input
#   model.
#
#   It should also be noted that this kind of model, while often used for face
#   landmarking, is quite general and can be used for a variety of shape
#   prediction tasks.  But here we demonstrate it only on a simple face
#   landmarking task.
#
# COMPILING/INSTALLING THE DLIB PYTHON INTERFACE
#   You can install dlib using the command:
#       pip install dlib
#
#   Alternatively, if you want to compile dlib yourself then go into the dlib
#   root folder and run:
#       python setup.py install
#
#   Compiling dlib should work on any operating system so long as you have
#   CMake installed.  On Ubuntu, this can be done easily by running the
#   command:
#       sudo apt-get install cmake
#
#   Also note that this example requires Numpy which can be installed
#   via the command:
#       pip install numpy

import os
import sys
import glob
import time
import datetime
import dlib

# In this example we are going to train a face detector based on the small
# faces dataset in the examples/faces directory.  This means you need to supply
# the path to this faces folder as a command line argument so we will know
# where it is.

faces_folder = "imgs"

options = dlib.shape_predictor_training_options()
# Now make the object responsible for training the model.
# This algorithm has a bunch of parameters you can mess with.  The
# documentation for the shape_predictor_trainer explains all of them.
# You should also read Kazemi's paper which explains all the parameters
# in great detail.  However, here I'm just setting three of them
# differently than their default values.  I'm doing this because we
# have a very small dataset.  In particular, setting the oversampling
# to a high amount (300) effectively boosts the training set size, so
# that helps this example.
#options.oversampling_amount = 300
# I'm also reducing the capacity of the model by explicitly increasing
# the regularization (making nu smaller) and by using trees with
# smaller depths.
#options.nu = 0.05
#options.tree_depth = 2
options.be_verbose = True

#DEFAULT VALUES
#https://medium.com/datadriveninvestor/training-alternative-dlib-shape-predictor-models-using-python-d1d8f8bd9f5c
# set the parameters
options.tree_depth = 5#file size
options.nu = 0.05#0.025#0.05#0.01#0.005#
#options.cascade_depth = 15 
#options.feature_pool_size = 1000#800#
#options.num_test_splits = 20#150#20#100#
#options.oversampling_amount = 40#20#80#
#options.num_threads = 16

#options.lambda_param = 0.01#0.005#

#options.num_trees_per_cascade_level = 500
#options.feature_pool_region_padding = 0
#options.oversampling_translation_jitter = 0  # available in the latest dlib release

#http://dlib.net/python/index.html#dlib.shape_predictor_training_options
#http://dlib.net/dlib/image_processing/shape_predictor_trainer_abstract.h.html#shape_predictor_trainer
#get_cascade_depth() == 10
#get_tree_depth() == 4
#get_num_trees_per_cascade_level() == 500
#get_nu() == 0.1
#get_oversampling_amount() == 20
#get_oversampling_translation_jitter() == 0
#get_feature_pool_size() == 400
#get_lambda() == 0.1
#get_num_test_splits() == 20
#get_feature_pool_region_padding() == 0
#get_random_seed() == ""
#get_num_threads() == 0
#get_padding_mode() == landmark_relative 


# dlib.train_shape_predictor() does the actual training.  It will save the
# final predictor to predictor.dat.  The input is an XML file that lists the
# images in the training dataset and also contains the positions of the face
# parts.
#training_xml_path = "H:/Facial Landmarks/mirror/all.xml"
#training_xml_path = "H:/Facial Landmarks/5 slow anim/data_out.xml"
training_xml_path = "../ibug_300W_large_face_landmark_dataset/labels_ibug_300W.xml"#"data_out_2to6.xml"
print(training_xml_path)

start = datetime.datetime.now()
print("start time : ", start)

dlib.train_shape_predictor(training_xml_path, "myPredictor.dat", options)

end = datetime.datetime.now()
print("endtime : ", end)
print("exec time : ", end - start)

# Now that we have a model we can test it.  dlib.test_shape_predictor()
# measures the average distance between a face landmark output by the
# shape_predictor and where it should be according to the truth data.
print("\nTraining accuracy: {}".format(
    dlib.test_shape_predictor(training_xml_path, "myPredictor.dat")))

exit()


# The real test is to see how well it does on data it wasn't trained on.  We
# trained it on a very small dataset so the accuracy is not extremely high, but
# it's still doing quite good.  Moreover, if you train it on one of the large
# face landmarking datasets you will obtain state-of-the-art results, as shown
# in the Kazemi paper.
testing_xml_path = os.path.join(faces_folder, "testing_with_face_landmarks.xml")
print("Testing accuracy: {}".format(
    dlib.test_shape_predictor(testing_xml_path, "myPredictor.dat")))


# Now let's use it as you would in a normal application.  First we will load it
# from disk. We also need to load a face detector to provide the initial
# estimate of the facial location.
predictor = dlib.shape_predictor("myPredictor.dat")
detector = dlib.get_frontal_face_detector()

# Now let's run the detector and shape_predictor over the images in the faces
# folder and display the results.
print("Showing detections and predictions on the images in the faces folder...")
win = dlib.image_window()
for f in glob.glob(os.path.join(faces_folder, "*.jpg")):
    print("Processing file: {}".format(f))
    img = dlib.load_rgb_image(f)

    win.clear_overlay()
    win.set_image(img)

    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))
        # Get the landmarks/parts for the face in box d.
        shape = predictor(img, d)
        print("Part 0: {}, Part 1: {} ...".format(shape.part(0),
                                                  shape.part(1)))
        # Draw the face landmarks on the screen.
        win.add_overlay(shape)

    win.add_overlay(dets)
    dlib.hit_enter_to_continue()

