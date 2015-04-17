
import os
import urllib, urllib2
import pyfits
from scipy.ndimage.filters import gaussian_filter
import shutil

import optparse

NVSS_URL='http://www.cv.nrao.edu/cgi-bin/postage.pl'
K7_SYNTH_BEAM = 4.0*60.0 # arcsec
NVSS_SYNTH_BEAM = 45.0 # arcsec

# --------------------------------------------------------------------------------------- 

def download_nvss_fits(nvss_dict):
 
    # download from NVSS postage server
    params = urllib.urlencode(nvss_dict)
    req = urllib2.Request(NVSS_URL,params)
    response = urllib2.urlopen(req)
   
    # save as fitsfile
    fitsfile = nvss_dict['ObjName']+'.fits' 
    with open(fitsfile, 'wb') as file:
        file.write(response.read())

    # return the name of the saved file
    return nvss_dict['ObjName']

# ---------------------------------------------------------------------------------------    

parser = optparse.OptionParser(usage="python %prog [options] csv_file", description='Download NVSS image and convolve to ~KAT-7 beam size. Sources listed in csv file provided, in rows of: source_name, right ascension, declination. Recommend keeping similar image and cell sizes to the default values, as too large an image will not download.')
parser.add_option("-s", "--stokes", default="I", help="Stokes parameter to download")
parser.add_option("-e", "--equinox", default="J2000", help="Equinox")
parser.add_option("-i", "--image-size", default="2.5 2.5", help="Image size (degrees). Default '2.5 2.5'")
parser.add_option("-c", "--cell-size", default="20.0 20.0", help="Cell size (arcseconds). Default '20.0 20.0'")
parser.add_option("-p", "--projection", default="SIN", help="Projection (default SIN)")
parser.add_option("-P", "--proxy", default=None, help="Proxy details, in a string of the form: http://username:password@proxy_url:port")
(options, args) = parser.parse_args()

# set proxy environment variable if provided
if options.proxy: os.environ['http_proxy'] = options.proxy

# set global image download parameters 
nvss_dict = {}
nvss_dict['PolType'] = options.stokes
nvss_dict['Equinox'] = options.equinox
nvss_dict['Size'] = options.image_size   
nvss_dict['Cells'] = options.cell_size   
nvss_dict['MAPROJ'] = options.projection
nvss_dict['Type'] = 'application/octet-stream'

# open file and read in each line
csv_file = file(args[0], "r") 
lines=csv_file.readlines()

# create directory for output and cd into it
output_dir = args[0].split('.')[0]
os.makedirs(output_dir)
os.chdir(output_dir)

# iterate through each line in the source file
for line in lines:
    # update image download parameters  for this source
    name, ra, dec = line.rstrip().split(',')
    nvss_dict['ObjName'] = name
    nvss_dict['RA'] = ra
    nvss_dict['Dec'] = dec

    # download the image
    filename = download_nvss_fits(nvss_dict)

    # copy to new file for convolving
    src = filename+'.fits'
    dest = filename+'_conv.fits'
    shutil.copyfile(src,dest)

    # open new file for convolved image
    conv_file = pyfits.open(dest,'update')
    # do the convolution
    conv_image = gaussian_filter(conv_file[0].data,K7_SYNTH_BEAM/NVSS_SYNTH_BEAM)
    # save convolved image data to new file
    conv_file[0].data = conv_image
    conv_file.close()









