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

'''
# "Exif.Photo.BodySerialNumber": "023021009293"
# "Exif.Canon.InternalSerialNumber": "AD0026822"
# "Exif.Canon.LensModel": "EF24-105mm f/4L IS USM",
# "Exif.Photo.LensSerialNumber": "00001061f2"
# "Exif.Canon.FirmwareVersion": "Firmware Version 1.0.7"
# "Exif.Photo.CameraOwnerName": ""
# "Exif.CanonCs.ISOSpeed": "15"
# "Exif.CanonSi.TargetAperture": "212"
# "Exif.Photo.LensSpecification": "24/1 105/1 0/1 0/1"
# "Exif.Nikon3.Lens": "70/1 200/1 280/100 280/100"
# "Xmp.aux.Lens": "70.0-200.0 mm f/2.8"
# "Xmp.aux.LensInfo": "70/1 200/1 280/100 280/100"
# "Exif.NikonLd3.LensIDNumber": "162"
# "Exif.Nikon3.LensFStops": "72 1 12 0"
# "Xmp.aux.SerialNumber": "2006688"
# "Exif.Nikon3.SerialNumber": "2006688"
# "Exif.NikonWt.Timezone": "0"
# 'Xmp.xmp.ModifyDate': "2010-02-11T15:35:55.00Z" <- weird time format
'''

class Camera:
	ISOSPEEDS = [64, 100, 200, 250, 320, 400, 640, 800, 1000, 1600, 3200]
	SHUTTERSPEEDS = [15, 30, 60, 125, 250, 400, 500, 1000, 1250, 1600, 2000, 4000]
	FSTOPS = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3.2, 3.4, 3.7, 4, 4.4, 4.8, 5.2, 5.6, 6.2, 6.7, 7.3, 8, 8.7, 9.5, 10, 11, 12, 14, 15, 16, 17, 19, 21, 22]
	def __init__(self):
		cameras = []
		self.hints = {
			'SerialTags': [
				'Exif.Photo.BodySerialNumber',
				'Exif.Canon.InternalSerialNumber',
				'Exif.Photo.LensSerialNumber',
				'Xmp.aux.SerialNumber',
				'Exif.Nikon3.SerialNumber'
			],
			'TimeFormats': {
				'nikonxmp':('\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\w', "%Y-%m-%dT%H:%M:%S.00Z"),
				'exif':('\d{4}:\d\d:\d\d \d\d:\d\d:\d\d', "%Y:%m:%d %H:%M:%S"),
				'gpstime':('\d+\/\d+\s+\d+\/\d+\s+\d+\/\d+', None)
			},
			'Randomize': {
				'Exif.Nikon3.ShutterCount': ('auto_randomize_integer', 0.5),
				'Exif.CanonSi.TargetAperture': ('auto_randomize_integer', 0.1),
				'Exif.NikonLd3.FocusDistance': ('auto_randomize_integer', 0.5),
				'Exif.NikonPc.Saturation': ('auto_randomize_integer', 0.25),
				'Exif.Photo.SubjectArea': ('auto_randomize_rect', None)
			},
			'FileNames': {
				'Canon': "IMG_0###.jpg",
				'NIKON CORPORATION': "dsc0###.jpg",
				'Sony':"mvc00###.jpg",
				'Apple':"IMG00###.jpg"
			}
		}
		self.time = None
		self.camera = None
		self.lens = None

		pass

	def load_json_dumps(self, indir):
		dumps = []
		for dumpfile in glob.glob(os.path.join(indir, "*.json")):
			with open(dumpfile) as df:
				dump = json.load(df)
				dumps.append(dump)
		return dumps

	def load_metadata(self, cameras, hints=None):
		# camera_makes = set([camera['Exif.Image.Make'] for camera in cameras])
		# models_for_make = set([camera['Exif.Image.Model'] for camera in cameras if camera['Exif.Image.Make'] == 'Canon'])
		# make_for_model = set([camera['Exif.Image.Make'] for camera in cameras if camera['Exif.Image.Model'] == u'Canon PowerShot G15'])
		self.cameras = self.load_json_dumps(cameras)
		if hints:
			self.hints = self.load_json_dumps(hints)
		print "Have %i cameras comprising %i unique makes and %i unique models." % (len(self.cameras), len(self.camera_makes()), len(self.camera_models()))
		for camera in self.cameras:
			print "%s: %s" % (camera['Exif.Image.Make'], camera['Exif.Image.Model'])
		return self

	def camera_makes(self):
		return set([camera['Exif.Image.Make'] for camera in self.cameras])

	def camera_models(self):
		return set([camera['Exif.Image.Model'] for camera in self.cameras])

	def fix_lens(self, camera):
		focal_length = Fraction(random.uniform(3.0, 75.0)).limit_denominator(2000)
		pass

	def randomize_filename(self, template):
		''' template###.jpg -> template783.jpg '''
		fname = str()
		for char in template:
			if char == '#':
				fname += str(random.randint(0, 9))
			else:
				fname += char
		return fname

	def auto_randomize_integer(self, camera, number, error=0.3):
		number = int(number)
		number = random.randint(int(number - (number * (error / 2.0))), int(number + (number * (error / 2.0))))
		if number < 0:
			number = 0
		return number

	def auto_randomize_rect(self, camera, unused_a, unused_b):
		dimx = int(camera['Exif.Photo.PixelXDimension'])
		dimy = int(camera['Exif.Photo.PixelYDimension'])
		rect = [random.randint(dimx/10, dimx/4), 
				random.randint(dimy/10, dimx/4),
				random.randint(dimx - (dimx/4), dimx - (dimx/10)),
				random.randint(dimy - (dimy/4), dimy - (dimy/10))]
		rect = " ".join([str(i) for i in rect])
		return rect

	def randomize_timestamp(self, start=(time.time() - 3.15569e7), end=time.time()):
		ts = random.randint(int(start), int(end))
		t = time.gmtime(ts)
		return t

	def randomize_serial(self, serial):
		newserial = str()
		for idx, char in enumerate(serial):
			if char.isalpha():
				maxchar = ord(char)
				minchar = ord('A') # fixme: find lowest character value in factory serial
				newserial += str(chr(random.randint(minchar, maxchar)))
			elif char.isdigit():
				maxchar = int(9)
				minchar = int(0) # fixme: find lowest character value in factory serial
				newserial += str(random.randint(minchar, maxchar))
			else:
				print "Weird character %02x in serial '%s' at position %i, leaving it alone." % (ord(char), serial, idx)
				newserial += char
		return newserial

	def replace_if_tag(self, tags, tag, value):
		if tag in tags.keys():
			tags[tag] = value

	def fix_serials(self, camera):
		''' file off the serial number '''
		for tag in self.hints['SerialTags']:
			if tag in camera.keys():
				print "Fixing serial: %s (%s)" % (tag, camera[tag])
				camera[tag] = self.randomize_serial(camera[tag])
		return camera

	def fix_timestamps(self, camera, newtime):
		skiptags = []
		for tag in camera.keys():
			if re.search('\w+Time\w+', tag):
				for fmtname, format in self.hints['TimeFormats'].iteritems():
					match = re.search(format[0], camera[tag])
					# print "%s - match:%s format[0]:'%s' format[1]:'%s' value:'%s'" % (fmtname, bool(match), format[0], format[1], camera[tag])
					if match and format[1]:
						print "%s: Fixing timestamp" % tag
						camera[tag] = time.strftime(format[1], newtime)
						skiptags = [t for t in skiptags if t != tag] # if we skipped it before, remove it from the skipped tag list now
					elif match and not format[1]:
						# FIXME add handlers for weird times like GPS's list of three rationals
						print "%s: Weird timestamp that can't be strftime()ed, skipping." % tag
						skiptags.append(tag)
					else:
						skiptags.append(tag)
		skiptags = list(set(skiptags))
		# blank out the skipped tags
		print skiptags
		for t in skiptags:
			camera[t] = ''

		return camera

	def fix_randomizable(self, camera):
		for tag, fnargs in self.hints['Randomize'].iteritems():
			fn = getattr(self, fnargs[0])
			if fn and (tag in camera.keys()):
				print "Randomizing %s with %s." % (tag, fnargs[0])
				camera[tag] = fn(camera, camera[tag], fnargs[1])
			else:
				if not fn:
					print "Attempt to randomize %s failed: no handler for %s." % (tag, fnargs[0])
		return camera

	def fix_exposure(self, camera, ev=None):
		# set the exposure parameters (shutter, aperture, flash)
		# FIXME randomize on EXIF time/estimated daylight with extra perturbations 
		# FIXME needs hints rough camera capabilities especially for P&S lines and phones
		# FIXME this is a top of the dome exposure "model"
		# FIXME this whole thing needs rework and thought
		aperture = Fraction(random.uniform(1.0, 16.0)).limit_denominator(2000)
		exposure = Fraction(1.0/round(random.randint(8, int(100.0*aperture))+1, -2)).limit_denominator(4000)
		camera['Exif.Photo.ISOSpeedRatings'] = str(random.choice(self.ISOSPEEDS))
		camera['Exif.Photo.ExposureTime'] = str(exposure)
		# shutter speed = -1*log2(exposure)
		# magic, i dunno.
		camera['Exif.Photo.ShutterSpeedValue'] = str(Fraction(math.log(exposure, 2) * -1).limit_denominator(2000))
		camera['Exif.Photo.ApertureValue'] = str(aperture)
		# f stop = sqrt(2)^aperture
		# more magic. looks real enough i think.
		camera['Exif.Photo.FNumber'] = str(Fraction(math.pow(1.4142, aperture)).limit_denominator(2000))

		flash = random.choice([0x00, 0x1, 0x18, 0x19, 0x49, 0x4d, 0x4f, 0x49, 0x4d, 0x4f])
		camera['Exif.Photo.Flash'] = str(flash)
		self.replace_if_tag(camera, 'Xmp.exif.Flash/exif:Fired', str(bool(flash & 0x01)))
		# camera['Exif.Photo.FocalLength'] = str(focal_length)
		camera['Exif.Image.Orientation'] = str(random.choice([0, 1]))
		return camera
		

	def fix_lens(self, camera):
		# set the lens
		# looks at hints for vendor and model-compatible lenses (as much as possible anyway)
		# at the very least should avoid putting a DSLR lens on an iPhone, because that's just silly
		return camera

	def set_camera(self, make=None, model=None):
		# set the camera
		# random make model if not specified
		# if both, make is ignored

		# TODO implement the above
		if self.cameras:
			self.camera = random.choice(self.cameras)
		else:
			self.camera = None
			return None

		return dict(self.camera)

	def snap(self):
		''' they pull they cameras out and god damn they snap '''
		# take a picture (generate an EXIF template based on the selected camera)
		cam = dict(self.camera)
		cam = self.fix_timestamps(cam, self.randomize_timestamp())
		cam = self.fix_serials(cam)
		cam = self.fix_exposure(cam)
		cam = self.fix_randomizable(cam)
		filename = self.randomize_filename(self.hints["FileNames"][cam['Exif.Image.Make']])
		return (cam, filename)

'''
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
'''

cameras = load_exif_dumps("exifdumps")
imgbuf = StringIO.StringIO()
cats = load_cats(cat_path)
assets = load_cats(asset_path)
katze = collage(2048, 1024, assets, cats, 10)
kexif = fix_image(katze, random.choice(cameras))
'''
# dump_exif("camrefs", "exifdumps")
cam = Camera()
cam.load_metadata("exifdumps")

import code
code.interact(local=locals())