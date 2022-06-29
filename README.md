# LST-camera validation
Scripts to do the tests for the validation of the LST cameras


# Rate scans
We need a bit more of information that is not saved by CaCo, this will be saved in a file called `extra_data.txt` organised like this,

```
date           HV         DAC     neighbor      gain
y-m-d-h:min:s  HV/not_HV  1/2/3   0/1/2/3/4/5   0/7/10/15/20
```
And this ones will be the runs that we are going to extract the data.

You need to have installed `PyPDF2` python package, that can be installed using `conda install -c conda-forge pypdf2` at conda console. Also you need the `lstchain` environement to be able to plot the information in the camera, visit https://github.com/cta-observatory/ctapipe for more information.

**How to use it**
- Copy `.results` files from CaCo to your computer, inside some folder `.../folder/`
- Copy the contents of the folder `rate_scans` in same directory


- Note: You need to have different packages installed so in order to use it you will need to install `PyPDF2` with `conda install -c conda-forge pypdf2`, and not strictly requiered but recommended to use `lstchain` or `ctapipe` environements, see https://github.com/cta-observatory/ctapipe

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
