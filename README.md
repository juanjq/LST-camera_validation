# LST-camera validation
Scripts to do the tests for the validation of the LST cameras


# Rate scans
We need a bit more of information that is not saved by CaCo, this will be saved in a file called `extra_data.txt` organised like this,

```
date         HV         DAC     neighbor      gain
y-m-d-h:m:s  HV/not_HV  1/2/3   0/1/2/3/4/5   0/7/10/15/20
```
And this ones will be the runs that we are going to extract the data.

You need to have installed `PyPDF2` python package
