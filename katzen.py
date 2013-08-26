# This Python file uses the following encoding: utf-8
import os
import os.path
import glob
import random
import json
import time
import re
import math
import string
import StringIO
import Image, ImageDraw, ImageFont
from gi.repository import GExiv2
from fractions import Fraction 

cat_path = "katze/"
asset_path = "assets/"

ISOSPEEDS = [64, 100, 200, 250, 320, 400, 640, 800, 1000, 1600, 3200]
SHUTTERSPEEDS = [15, 30, 60, 125, 250, 400, 500, 1000, 1250, 1600, 2000, 4000]
FSTOPS = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3.2, 3.4, 3.7, 4, 4.4, 4.8, 5.2, 5.6, 6.2, 6.7,
          7.3, 8, 8.7, 9.5, 10, 11, 12, 14, 15, 16, 17, 19, 21, 22]
'''
class Camera:
	def __init__(self):
		vendors = []
		cameras = []
		camera=None
		pass

	def load_metadata(self, vendors, cameras):
		# camera_makes = set([camera['Exif.Image.Make'] for camera in cameras])
		# models_for_make = set([camera['Exif.Image.Model'] for camera in cameras if camera['Exif.Image.Make'] == 'Canon'])
		# make_for_model = set([camera['Exif.Image.Make'] for camera in cameras if camera['Exif.Image.Model'] == u'Canon PowerShot G15'])
		pass

	def camera(self):
		# set the camera
		pass

	def randomize(self):
		# pick a random camera
		pass

	def snap(self, camera=None):
		# take a picture (generate an EXIF template based on the selected camera)
		pass

class Tourist:
	def __init__(self):
		locations = []
		pass

	def randomize(self):
		# pick a random point of interest
		pass

'''


def load_cats(path):
	cat_pics = []
	for imgfile in glob.glob(os.path.join(path, "*.jpg")):
		print "Loading cat: " + imgfile
		cat = Image.open(imgfile)
		cat.thumbnail((640, 480))
		cat = cat.convert('RGBA')
		cat_pics.append(cat)
	return cat_pics

def mangle_cat(image):
	# TODO mess with image
	#image = image.convert('RGB')
	#image = image.convert('P', palette=Image.ADAPTIVE, colors=2*random.randint(1,128))
	return image.convert('RGBA')

def mangle_collage(image):
	return image.convert('RGBA')

def collage(width, height, backgrounds, cats, count):
	collage = Image.new('RGBA', (width, height), "white")
	bg = random.choice(backgrounds).copy().resize((width, height)).rotate(random.uniform(-2.0, 2.0), Image.BICUBIC, expand=1)
	collage.paste(bg, (0,0), mask=bg)

	for i in range(0, count):
		copy_cat = random.choice(cats).copy()
		copy_cat = mangle_cat(copy_cat)
		scale = random.uniform(0.5, 2.0)
		top = random.randint(-64, width - 64)
		left = random.randint(-64, height - 64)

		copy_cat.putalpha(random.randint(64, 255))
		copy_cat = copy_cat.rotate(random.uniform(0.0, 360.0), Image.BICUBIC, expand=1)
		copy_cat = copy_cat.resize((int(copy_cat.size[0] * scale), int(copy_cat.size[1] * scale)), Image.ANTIALIAS)
		collage.paste(copy_cat, (top,left), mask=copy_cat)
	return mangle_collage(collage)

def text_overlay(image, strings, fonts, minsize=10, maxsize=72):
	ctx = ImageDraw.Draw(image)
	font = ImageFont.truetype("font.ttf", 72)
	ctx.text((100,100), "cats cats cats", font=font, fill=0xFF000000)
	return image

def dump_exif(indir, outdir, clobber=False):
	for imgfile in glob.glob(os.path.join(indir, "*.jpg")):
		exif = GExiv2.Metadata(imgfile)
		exif_dict = dict(zip(exif.get_tags(), [exif[tag] for tag in exif.get_tags()]))
		tag_json = json.dumps(exif_dict, indent=4, separators=(',', ': '))
		
		exif_dumpfile = ".".join([os.path.basename(imgfile).split('.')[0], "json"])
		if not os.path.isfile(exif_dumpfile) or clobber:
			print "Writing EXIF dump for %s %s %s %s" % (imgfile, exif_dict['Exif.Image.Make'], exif_dict['Exif.Image.Model'], "(overwritten)" if clobber else "")
			if not os.path.exists(outdir):
				os.makedirs(outdir)

			with open(os.path.join(outdir, exif_dumpfile), 'w+') as df:
				df.write(tag_json)
		else:
			print "EXIF dump already exists for %s, skipping" % imgfile

def load_exif_dumps(indir):
	dumps = []
	for dumpfile in glob.glob(os.path.join(indir, "*.json")):
		with open(dumpfile) as df:
			dump = json.load(df)
			dumps.append(dump)
	return dumps

def random_timestamp(start=(time.time() - 3.15569e7), end=time.time()):
	return time.gmtime(random.randint(int(start), int(end)))



def replaceiftag(tags, tag, value):
	if tag in tags.keys():
		tags[tag] = value

def fix_exif(image_exif, template_exif_dump, metalocation=None, metacamera=None):
	''' fix as in fixer '''
	# image_exif is a gexiv2 metadata object
	# template_exif is a json exif dump
	template = dict(template_exif_dump)
	imgtime = time.strftime("%Y:%m:%d %H:%M:%S", random_timestamp())

	template_tags = template.keys()
	dimx = int(template['Exif.Photo.PixelXDimension'])
	dimy = int(template['Exif.Photo.PixelYDimension'])

	# date/time properties
	template['Exif.Photo.DateTimeOriginal'] = imgtime
	template['Exif.Photo.DateTimeDigitized'] = imgtime
	template['Exif.Image.DateTime'] = imgtime
	replaceiftag(template, 'Xmp.exif.DateTimeDigitized', imgtime)
	replaceiftag(template, 'Xmp.exif.DateTimeOriginal', imgtime)

	# photograpic properties
	# FIXME this should map back to a database of rough camera capabilities
	# especially for P&S lines and phones
	focal_length = Fraction(random.uniform(3.0, 75.0)).limit_denominator(2000)
	# FIXME this is a top of the dome exposure model
	aperture = Fraction(random.uniform(1.0, 10.0)).limit_denominator(2000)
	exposure = Fraction(1.0/round(random.randint(8, int(100.0*aperture)), -2)).limit_denominator(4000)
	template['Exif.Photo.ISOSpeedRatings'] = str(random.choice(ISOSPEEDS))
	template['Exif.Photo.ExposureTime'] = str(exposure)
	# shutter speed = -1*log2(exposure)
	# magic, i dunno.
	template['Exif.Photo.ShutterSpeedValue'] = str(Fraction(math.log(exposure, 2) * -1).limit_denominator(2000))
	template['Exif.Photo.ApertureValue'] = str(aperture)
	# f stop = sqrt(2)^aperture
	# more magic. looks real enough i think.
	template['Exif.Photo.FNumber'] = str(Fraction(math.pow(1.4142, aperture)).limit_denominator(2000))

	if 'Exif.Photo.SubjectArea' in template_tags:
		# make a box. i dunno
		subjarea = [random.randint(dimx/10, dimx/4), 
					random.randint(dimy/10, dimx/4),
					random.randint(dimx - (dimx/4), dimx - (dimx/10)),
					random.randint(dimy - (dimy/4), dimy - (dimy/10))]
		template['Exif.Photo.SubjectArea'] = " ".join([str(i) for i in subjarea])
	flash = random.choice([0x00, 0x1, 0x18, 0x19, 0x49, 0x4d, 0x4f, 0x49, 0x4d, 0x4f])
	template['Exif.Photo.Flash'] = str(flash)
	replaceiftag(template, 'Xmp.exif.Flash/exif:Fired', str(bool(flash & 0x01)))
	template['Exif.Photo.FocalLength'] = str(focal_length)
	template['Exif.Image.Orientation'] = str(random.choice([0, 1]))

	image_exif.clear()
	for tag, value in template.iteritems():
		image_exif[tag] = value

	return image_exif

def fix_image(image, template_exif):
	temp = os.tmpnam()
	scalex = template_exif['Exif.Photo.PixelXDimension']
	scaley = template_exif['Exif.Photo.PixelYDimension']
	image = image.resize((int(scalex), int(scaley)), Image.ANTIALIAS)
	image.save(temp, "JPEG")
	image_exif = GExiv2.Metadata(temp)
	image_exif = fix_exif(image_exif, template_exif)
	image_exif.save_file()
	return temp
	
dump_exif("camrefs", "exifdumps")
cameras = load_exif_dumps("exifdumps")
imgbuf = StringIO.StringIO()
cats = load_cats(cat_path)
assets = load_cats(asset_path)
katze = collage(2048, 1024, assets, cats, 10)
kexif = fix_image(katze, random.choice(cameras))
import code
code.interact(local=locals())