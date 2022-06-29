# LST-camera validation
Scripts to do the tests for the validation of the LST cameras


# Rate scans: instructions to use

- Copy `.results` files from CaCo to your computer, inside some folder `.../folder/`

- Copy the contents of the folder `rate_scans` all in same directory

- Note: You need to have different packages installed so in order to use it you will need to install `PyPDF2` with `conda install -c conda-forge pypdf2`, and not strictly requiered but recommended to use `lstchain` or `ctapipe` environements, see https://github.com/cta-observatory/ctapipe

- We need more information than what's inside the files, that we do not have in CaCo, this need to be written by hand in a file called `extra_data.txt` organised like this, (example file used in LST-1 in the folder `rate_scans`)

```
date           HV         DAC     neighbor      gain
y-m-d-h:min:s  HV/not_HV  1/2/3   0/1/2/3/4/5   0/7/10/15/20
```
And this ones will be the runs that we are going to extract the data.

- Once we have this we open the notebook `main.ipynb`, and complete the parameters section

# Dark pedestal & pedestal with background

# Pedestal recovery


# CrossTalk


# Deadtime and Readout
Here I only did the script to extract the times data of a run, i.e. the time where the events happen, not any more information. That is the information we need to perform the Deadtime analysis

# Camera plots

### Geometry indexation

# Historical monitoring

# Other things done
### BP calibration scripts
