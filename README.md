# Running on Binder (Recommended for Windows users):

1. Klick here: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/teokem/responseStudies-alex-exook/HEAD)
 * The build takes a long time ~10 min
 * If it gets stuck at "Successfully pushed XXXXX", refresh the page and it should find an already built image and launch within a minute
2. When the Binder server is running, before opening the jupyter notebook, start a terminal to extract and decrypt data.zip.
 * On the right there is a drop-down menu called "New", click it and select "Terminal". A new browser tab will open with a command line.
 * Enter: `7z x data.zip` into the terminal. When prompted, enter the password given to you by me. This will extract and decrypt the data for the notebook.
 * Close the terminal browser tab.
3. Open the jupyter notebook `responseStudies.ipynb`, and follow the instructions there.
 * In the notebook, you can run each cell of code/text one by one by using `shift`+`enter`. This will give you a chance to read the text and understand the code. To run everything from top to bottom in one go, press :fast_forward: in the top toolbar to restart and run the whole notebook

# Running Locally (Linux):

To run this notebook locally you will need Conda or miniconda, as well as p7zip.
* To install miniconda follow the instructions found here: https://docs.conda.io/en/latest/miniconda.html
* To install p7zip do: `sudo apt-get install p7zip-full`

1. Clone this repository\
`git clone https://github.com/teokem/responseStudies-alex-exook.git`
3. Enter the newly cloned directory\
`cd responseStudies-alex-exook`
4. Download the encrypted data\
`wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=19Dv4JkJEqi-tzT33wjAvtufNqcwi8Lr0' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=19Dv4JkJEqi-tzT33wjAvtufNqcwi8Lr0" -O data.zip && rm -rf /tmp/cookies.txt`
5. Decrypt the encrypted data\
`z x data.zip`
6. Create the python environment using conda\
`conda env create -f environment.yml`
7. Activate the newly created environment\
`conda activate responsePlotting`
8. Open the notebook `responseStudies.ipynb`, and follow the instructions there\
`jupyter notebook`
 * In the notebook, you can run each cell of code/text one by one by using `shift`+`enter`. This will give you a chance to read the text and understand the code. To run everything from top to bottom in one go, press :fast_forward: in the top toolbar to restart and run the whole notebook

# Environment Packages
* The python and notebook packages are required to run the code in the current notebook format
* ROOT is required to read and fit the data with the root framework tools developed at CERN
* Numpy is used for the numpy array data structure
* Pandas is used for the data frame data structure, which is crucial for keeping the different data series, and slices of data series organized
* Scipy is used for curve fitting
* Matplotlib is used for plotting
* Bokeh is used for interactive plotting
* Mplhep is required for the ATLAS experiment specific plot styling
