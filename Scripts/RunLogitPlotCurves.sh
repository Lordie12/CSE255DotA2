#!/bin/bash

# Delete the NPZ files and the model pickled
# rm -rf ../Logit/*.npz
# rm -rf ../Logit/*.pkl
# Create the preprocessed data set
# python preprocess.py
# Run the Training algorithm
# python LogitTrain.py
# Plot the accuracy vs. sample size curve
python plotCurves.py