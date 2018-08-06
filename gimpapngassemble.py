#!/usr/bin/env python

from gimpfu import *
import os
import json
from os import unlink, listdir, chdir
from os.path import isfile, join
import subprocess

asm = 'apngasm'
s = '-s'
l = '-l'
combine = ''
metafile = 'layermeta.json'

formstr = ' {0}'

def get_pngs(path):
  tmp = [i for i in listdir(path) if isfile(join(path, i))]
  tmp2 = [y for y in tmp if '.png' in y]
  tmp2.sort()
  return tmp2

def assemble_apng(img, drw, filename, filepath, skip, loop):
	# removing potential previous animations
	outfile = os.path.join(filepath, filename)
	pl = get_pngs(filepath)

	chdir(filepath)
	for i in pl:
		if isfile(i):
			unlink(i)

	# create frames and data
	pdb.python_fu_export_image_layers(img, drw, filepath)

	# write command line
	metaoutfile = join(filepath, metafile)
	pnglist = get_pngs(filepath)

	## configuration
	global asm
	cmdline = []
	cmdline.append(asm)
	if skip:
		cmdline.append(s)
	if loop>0:
		cmdline.append(l)
		cmdline.append(loop)

	## frames
	with open(metaoutfile, 'r') as fmeta:
		framedata = json.load(fmeta)
	for i in pnglist:
		md = framedata[i]
		cmdline.append(i)
		dur = int(md[0])
		cmdline.append(str(dur))

	pdb.gimp_message(cmdline)

	# assemble animation
	subprocess.call(cmdline)

register(
	"assemble_apng",
	"create an animated PNG",
	"take a list of frames and metadata and create an animated PNG with an external assembler",
	"me",
	"me",
	"2018",
	"<Image>/Python-Fu/APNGAssembler",
	"* or RGB* or other filetype",
	[
	(PF_FILENAME, "filename", "Output file", "output.png"),
	(PF_DIRNAME, "filepath", "Output directory", "/tmp"),
	(PF_BOOL,    "skip" ,"First frame is not part of the animation", True),
	(PF_SPINNER, "loop"  ,"Times the animation loops (0=infinite)",0,(0,100,1))
	],
	[],
	assemble_apng)

main()
