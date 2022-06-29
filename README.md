# LST-camera validation
Scripts to do the tests for the validation of the LST cameras


# Rate scans analysis: instructions to use
---

1. Copy `.results` files from CaCo to your computer, inside some folder `.../folder/`

2. Copy the contents of the folder `rate_scans` all in same directory, that where we are going to run the script

3. We need more information than what's inside the files, that we do not have in CaCo, this needs to be written by hand in a file called `extra_data.txt` organised like this, (example file used in LST-1 in the folder `rate_scans`)

```
date           HV         DAC     neighbor      gain
y-m-d-h:min:s  HV/not_HV  1/2/3   0/1/2/3/4/5   0/7/10/15/20
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; And this ones will be the runs that we are going to extract the data. Put this file in same directory of the scripts.

4. Note: You need to have installed `PyPDF2` package, you can do it with `conda install -c conda-forge pypdf2`, and also not strictly requiered but recommended to use `lstchain` or `ctapipe` environements, see https://github.com/cta-observatory/ctapipe

5. Once we have this, we open the notebook `main.ipynb`, and complete the requiered parameters,
    - `data_type`, we use `='l0'` if we want to analyse the l0 or ipr runs (pixel analysis), and `='l1'` for the l0 data (cluster analysis)
    - `data_path`, the full directory name where we have the rate scans data (without final '/'), for example, `'/data/cta/users-ifae/summer_students/jjimenezq'`
    - Other configuration is explained in the notebook, but is not necessary to change

6. Run all the notebook. Plots will be generated in a folder called `output` in same directory

---
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
