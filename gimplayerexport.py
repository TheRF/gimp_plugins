#!/usr/bin/env python

from gimpfu import *
import re
import os
import json

durationpattern = re.compile('[(](\d+)?ms[)]')
combinepattern = re.compile('[(]([a-z]+)?[)]')
exclpattern = re.compile('[(][!][)]')
metadata = {}
j = -1
layercount = 0
fpath = ''

def count_layers(layer):
	if pdb.gimp_item_is_group(layer):
		for i in layer.layers:
			count_layers(i)
	else:
		global j
		j = j+1

def export_layer(img, layer):
	if pdb.gimp_item_is_group(layer):
		for i in layer.layers:
			export_layer(img, i)
	else:
		# get frame data from layer
		name = layer.name

		# duration for animations
		mat = durationpattern.search(name)
		num = '100'
		if mat:
			num = mat.group(1)
		pdb.gimp_message('duration is: '+num)

		# state of image (replace, combine), ignored by apng
		mat = combinepattern.search(name)
		comb = 'replace'
		if mat:
			comb = mat.group(1)
		pdb.gimp_message('frame state is: '+comb)

		mat = exclpattern.search(name)
		excl = False
		if mat:
			excl = True

		# copy layer to new image and save
		h = pdb.gimp_image_height(img)
		w = pdb.gimp_image_width(img)
		simg = pdb.gimp_image_new(w, h, 0)
		simg.new_layer()
		slay = simg.layers[0]

		pdb.gimp_edit_copy(layer)
		floating = pdb.gimp_edit_paste(simg.layers[0], 0)
		pdb.gimp_floating_sel_anchor(floating)

		# save png and meta data
		global j
		z = 1
		y = layercount
		while y>10:
			y = y//10
			if y>0:
				z+=1

		fileform = '{:0'+str(z)+'d}'
		outfile = fileform.format(j)+'.png'
		outfilefull = os.path.join(fpath, outfile)
		pdb.gimp_message('outfile is: '+outfile)

		pdb.gimp_file_save(simg, slay, outfilefull, '?')

		# storing metadata of layer for later animation assembly
		metalist = [num, comb]
		if excl:
			metalist.append('!')
		metadata[outfile] = metalist

		j = j-1
		pdb.gimp_image_delete(simg)

def export_image_layers(img, tdrawable, filepath):
	if len(img.layers)<1:
		pdg.gimp__message('not enough layers')
		return

	global fpath
	fpath = filepath

	# get proper layer count so we can name the frames
	# bottom up akin to how gif animations are assembled
	for i in img.layers:
		count_layers(i)

	global layercount
	layercount = j+1

	# export every frame as a png
	for i in img.layers:
		export_layer(img, i)

	# save metadata alongside frames
	metaoutfile = os.path.join(filepath, 'layermeta.json')
	with open(metaoutfile, 'w') as jsonfile:
		json.dump(metadata, jsonfile)

register(
	"export_image_layers",
	"export layers of image",
	"takes every frame of an image and stores it in a file. Also exports metadata as well",
	"me",
	"me",
	"2018",
	"<Image>/Python-Fu/LayerExporter",
	"* or RGB* or other filetype",
	[
	(PF_DIRNAME, "filepath", "Output directory", "/tmp")
	],
	[],
	export_image_layers)

main()
