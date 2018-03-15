import os
import time
import re
from PySide import QtGui, QtCore

software_version = "0.3.55"

keyring_servicename = "wbashotgun"
import_file_types = ['psd','psb','ma','mb','mov','jpg','JPG','pdf','tga','png','skp','tif','mp4','fla']

'''

Lots of info here...


'''


class wbaShotgun(object):


# 	A Shotgun support Class
# 	---------------------------------------------------------------
# 	Inputs
# 
# 	sg				{object}			Current Shotgun connection instance from Application
# 	debug			boolean				Debug flag
# 
# 	assetType(self,asset_name,asset_project_name)
# 	parseFilename(self,file_name,wba_projects)
# 	publishedFileExists(self,pub_file_name)
# 	wba_projects(self)


	def __init__ (self, sg, debug):
			
		self.sg = sg
		self.debug = debug
		
		import os

				
	def parseFilename(self,file_name,wba_projects):
	
# 	This module parses WBA filenames into tokens and returns information based on naming conventions.
# 	It does NOT authenticate any tokens with Shotgun.
# 	
# 	parseFilename returns a Dictionary of parsed key:value pairs including the 'errors' key which contains
# 	a list of error strings.
# 	
# 	It first tries to determine Shot vs. Asset by examining the first part of the filename string. 
# 	
# 	Shot Patterns
# 	
# 	Episode_Sequence_ShotNumber		XXXX####_X##_####		LGDC205_A01_1010
# 	Episode_Sequence_ShotNumber		XXXX####_###_####		LGDC205_001_1010
# 	Sequence_ShotNumber_Episode		X##_####_XXXX####		A01_1010_LGDC205
# 	Sequence_ShotNumber_Episode		###_####_XXXX####		A01_1010_LGDC205
# 	
# 	Asset Patterns
# 	
# 	XXXX####_@@@@@@@@				XXXX####_AssetName		LGDC205_AssetName
# 	XXXX_@@@@@@@@					XXXX_AssetName			LGDC_AssetName
# 	
# 	
# 	If it matches a Shot or Asset 'prefix' remove the prefix and from the filename and scan through the rest of the tokens.
# 	
# 	Task Patterns
# 	
# 	Xx			An
# 	
# 	Version Number Patterns
# 	
# 	vWBAVersionxVendorVersion		v##x##			v01x01
# 	vWBAVersionVendorVersion		v####			v0101
# 	vWBAVersion						v##				v01
# 	vWBAVersion						v###			v001
# 	xVendorVersion					x##				x01
# 	
# 	
# 	The first token that does not match a Task Token or Version Number is set as the Extra Token.
# 
# 
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	file_name				str					Filename to parse. Just the filename, not the path.
# 	wba_projects			dict				WBA Project Configurations
	

	
		self.file_name = file_name
		self.wba_projects = wba_projects
		
		self.project_code = ''
		self.optional_token = ''
		self.version_style = 'Normal'
		
		self.parsed_filename = {}
		self.parsed_filename['errors'] = []
		
				
	# File Extension

		try:																		
			self.temp_version_name,self.file_extension = self.file_name.rsplit('.',1)
			self.parsed_filename['file_extension'] = self.file_extension		
		except:
			self.temp_version_name = self.file_name
# 			self.parsed_filename['version_name'] = self.version_name
			self.parsed_filename['file_extension'] = ''
			self.parsed_filename['errors'].append('NO FILE EXTENSION')

	# Split into Tokens
	
		try:
			self.all_tokens = self.temp_version_name.split('_')
		except :
			pass
			self.parsed_filename['errors'].append('Cannot split filename into Tokens')
			
	# Shot
		
		#	Normal CG      LGDC208_A01_1010_     LGDC208_001_1010_
		if re.match('^[A-Z]{4}[0-9]{3}_[A-Z]{1}[0-9]{2}_[0-9]{4}_',self.temp_version_name) or re.match('^[A-Z]{4}[0-9]{3}_[0-9]{3}_[0-9]{4}_',self.temp_version_name) is not None:			 		
			self.parsed_filename['type'] = 'Shot'
			self.parsed_filename['episode_name'] = self.all_tokens[0]
			self.project_code = self.parsed_filename['episode_name'][:4]
			self.parsed_filename['asset_name'] = '%s_%s_%s' % (self.all_tokens[0],self.all_tokens[1],self.all_tokens[2])
			self.post_asset = self.temp_version_name.replace(self.parsed_filename['asset_name']+'_','')
						
		#	WBA DDR        A01_1010_LGDC208_     001_1010_LGDC208_
		elif re.match('^[A-Z]{1}[0-9]{2}_[0-9]{4}_[A-Z]{4}[0-9]{3}_',self.temp_version_name) or re.match('^[0-9]{3}_[0-9]{4}_[A-Z]{4}[0-9]{3}_',self.temp_version_name) is not None:			
			self.parsed_filename['type'] = 'Shot'
			self.parsed_filename['episode_name'] = self.all_tokens[2]
			self.project_code = self.parsed_filename['episode_name'][:4]
			self.parsed_filename['asset_name'] = '%s_%s_%s' % (self.all_tokens[0],self.all_tokens[1],self.all_tokens[2])
			self.post_asset = self.temp_version_name.replace(self.parsed_filename['asset_name']+'_','')

		#	Old CG 2-char Project Codes     LD194_A01_1010_
		elif re.match('^[A-Z]{2}[0-9]{3}_[A-Z]{1}[0-9]{2}_[0-9]{4}_',self.file_name) is not None:			 
			self.parsed_filename['episode_name'] = self.all_tokens[0]
			self.parsed_filename['type'] = 'Shot'
			self.project_code = self.parsed_filename['episode_name'][:2]
			self.parsed_filename['asset_name'] = '%s_%s_%s' % (self.all_tokens[0],self.all_tokens[1],self.all_tokens[2])
			self.post_asset = self.temp_version_name.replace(self.parsed_filename['asset_name']+'_','')
			
	# Not Shot
			
		else :
							
			#   Episode based Asset		LGDC208_
			if re.match('^[A-Z]{4}[0-9]{3}_',self.temp_version_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['episode_name'] = self.all_tokens[0]
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.parsed_filename['episode_name'][:4]
				self.post_asset = self.temp_version_name.replace(self.project_code+'_'+self.parsed_filename['asset_name']+'_','')
			
			#   Project based Asset		LGDC_
			elif re.match('^[A-Z]{4}_',self.temp_version_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.all_tokens[0][:4]
				self.post_asset = self.temp_version_name.replace(self.project_code+'_'+self.parsed_filename['asset_name']+'_','')

			#   OLD Episode based Asset		LD194_
			elif re.match('^[A-Z]{2}[0-9]{3}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['episode_name'] = self.all_tokens[0]
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.all_tokens[0][:2]
				self.post_asset = self.temp_version_name.replace(self.project_code+'_'+self.parsed_filename['asset_name']+'_','')

			#   OLD Project based Asset		LD_
			elif re.match('^[A-Z]{2}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.all_tokens[0][:2]
				self.post_asset = self.temp_version_name.replace(self.project_code+'_'+self.parsed_filename['asset_name']+'_','')

	# Project
				
		if self.project_code != "" :
			for self.wba_project_name in self.wba_projects.keys() :
				if 'wba_project_code' in self.wba_projects[self.wba_project_name] :				
					if  self.project_code == self.wba_projects[self.wba_project_name]['wba_project_code'] :
						self.parsed_filename['project_name'] = self.wba_project_name

					
	# Look for prefix-less Version Tokens at end of filename
					
		#    DDR based Take and Version Numbers		_01_01
		if re.search('_[0-9]{2}_[0-9]{2}$',self.post_asset) is not None:		
			try:
				self.post_asset.rsplit('_',2)[1]
				ddr_wba_version = self.post_asset.rsplit('_',2)[1]
				ddr_vendor_version = self.post_asset.rsplit('_',2)[2]
				ddr_version_token = "_"+ddr_wba_version+"_"+ddr_vendor_version
				self.parsed_filename['wba_version'] = int(ddr_wba_version)
				self.parsed_filename['vendor_version'] = int(ddr_vendor_version)
				self.post_asset = self.post_asset.replace(ddr_version_token,'')
				self.parsed_filename['version_number_style'] = 'DDR'
				self.version_style = 'DDR'
											
			except : pass
														
	# Loop through all remaining tokens...
	
		self.all_post_asset_tokens = self.post_asset.split('_')		
		for self.post_asset_token in self.all_post_asset_tokens :
			if self.post_asset_token != '' :
		
		# Task Token
						
				if re.match('^[A-Z]{1}[a-z]{1}$',self.post_asset_token) is not None:
					if 'wba_task_tokens' in self.wba_projects[self.parsed_filename['project_name']] :
						for self.check_task_token,self.check_task_name in self.wba_projects[self.parsed_filename['project_name']]['wba_task_tokens'].iteritems():
							if self.post_asset_token == self.check_task_token :
								self.parsed_filename['task_name'] = self.check_task_name
								self.parsed_filename['task_token'] = self.check_task_token
		# Version Numbers
									
				elif re.match('^v[0-9]{2}x[0-9]{2}$',self.post_asset_token) is not None:								#    v01x01					
					self.parsed_filename['wba_version'] = int(self.post_asset_token[1]+self.post_asset_token[2])
					self.parsed_filename['vendor_version'] = int(self.post_asset_token[4]+self.post_asset_token[5])
					self.parsed_filename['version_number_style'] = 'Normal'
					
				elif re.match('^v[0-9]{2}[0-9]{2}$',self.post_asset_token) is not None:									#    v0101					
					self.parsed_filename['wba_version'] = int(self.post_asset_token[1]+self.post_asset_token[2])
					self.parsed_filename['vendor_version'] = int(self.post_asset_token[3]+self.post_asset_token[4])
					self.parsed_filename['version_number_style'] = 'OLD'
					self.version_style = 'OLD'
					
				elif re.match('^x[0-9]{2}$',self.post_asset_token) is not None:											#    x01					
					self.parsed_filename['vendor_version'] = int(self.post_asset_token[1]+self.post_asset_token[2])
					self.parsed_filename['version_number_style'] = 'Separate'
					self.version_style = 'Separate'
					
				elif re.match('^v[0-9]{2}$',self.post_asset_token) is not None:											#    v01					
					self.parsed_filename['wba_version'] = int(self.post_asset_token[1]+self.post_asset_token[2])
					self.parsed_filename['version_number_style'] = 'Separate'
					self.version_style = 'Separate'

				elif re.match('^v[0-9]{3}$',self.post_asset_token) is not None:											#    v001					
					self.parsed_filename['wba_version'] = int(self.post_asset_token[1]+self.post_asset_token[2]+self.post_asset_token[3])
					self.parsed_filename['version_number_style'] = 'Separate'
					self.version_style = 'Separate'
													
				else:
					if self.optional_token == '' :
						self.parsed_filename['extra_token'] =  self.post_asset_token
						self.optional_token = self.post_asset_token

		
	# Create Version Name from parsed dictionary
			
		if 'wba_project_code' in self.wba_projects[self.parsed_filename['project_name']] :
			self.parsed_filename['project_code'] = self.wba_projects[self.parsed_filename['project_name']]['wba_project_code']
							
		self.version_name = self.createVersionName(self.parsed_filename)
						
		if self.debug :

			print "\n   Parsed file_name:",self.file_name
			print "--------------------------------------------------------------------------------"
			if 'project_name' in self.parsed_filename.keys() : print "        project_name:",self.parsed_filename['project_name']
			if 'episode_name' in self.parsed_filename.keys() : print "        episode_name:",self.parsed_filename['episode_name']
			if 'asset_name' in self.parsed_filename.keys() : print "          asset_name:",self.parsed_filename['asset_name']
			if 'type' in self.parsed_filename.keys() : print "                type:",self.parsed_filename['type']
			if 'asset_type' in self.parsed_filename.keys() : print "          asset_type:",self.parsed_filename['asset_type']
			if 'version_name' in self.parsed_filename.keys() : print "        version_name:",self.parsed_filename['version_name']
			if 'extra_token' in self.parsed_filename.keys() : print "         extra_token:",self.parsed_filename['extra_token']
			if 'task_name' in self.parsed_filename.keys() : print "           task_name:",self.parsed_filename['task_name']
			if 'task_token' in self.parsed_filename.keys() : print "          task_token:",self.parsed_filename['task_token']
			if 'wba_version' in self.parsed_filename.keys() : print "         wba_version:",self.parsed_filename['wba_version']
			if 'vendor_version' in self.parsed_filename.keys() : print "      vendor_version:",self.parsed_filename['vendor_version']
			if 'file_extension' in self.parsed_filename.keys() : print "      file_extension:",self.parsed_filename['file_extension']
			if 'errors' in self.parsed_filename : print "              errors:",'\n'.join(self.parsed_filename['errors'])
			print "--------------------------------------------------------------------------------"
									
		return (self.parsed_filename)	


	def createVersionName(self,parsed_filename):

# 	Returns a Version name in string form based on parsed input dictionary.
# 	Return 'None' string if a proper Version name can not be fashioned from supplied dictionary.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	parsed_filename				dict					Dictionary of parsed information from parseFilename()
	

		
		self.parsed_filename = parsed_filename	
		self.version_name = ''
		
		if 'version_number_style' in self.parsed_filename :
			self.version_style = self.parsed_filename['version_number_style']
		else :
			self.version_style = 'Normal'
	
		if 'type' in self.parsed_filename :
			if self.parsed_filename['type'] == 'Asset' :
				if 'episode_name' in self.parsed_filename and 'asset_name' in self.parsed_filename :
					self.version_name += self.parsed_filename['episode_name']+'_'+self.parsed_filename['asset_name']
				elif 'asset_name' in self.parsed_filename :
					self.version_name += self.parsed_filename['project_code']+'_'+self.parsed_filename['asset_name']

	# Shots need episode_name
		
			if self.parsed_filename['type'] == 'Shot' :
				if 'episode_name' in self.parsed_filename :
					if 'asset_name' in self.parsed_filename :
						self.version_name += self.parsed_filename['asset_name']				
				else :
					print "\nWARNING! createVersionName error..."
					print "shot"
					return None
													
			if 'task_token' in self.parsed_filename :
				self.version_name += '_'+self.parsed_filename['task_token']
								
			if 'wba_version' in self.parsed_filename :
				if self.version_style == 'DDR' :
					self.version_name += '_'+str(self.parsed_filename['wba_version']).zfill(2)+'_'+str(self.parsed_filename['vendor_version']).zfill(2)
				
				else:
					self.version_name += '_v'+str(self.parsed_filename['wba_version']).zfill(2)
					if 'vendor_version' in self.parsed_filename :
						if self.version_style == 'Normal' :
							self.version_name += 'x'+str(self.parsed_filename['vendor_version']).zfill(2)
						if self.version_style == 'OLD' :
							self.version_name += str(self.parsed_filename['vendor_version']).zfill(2)
						if self.version_style == 'Separate' :
							self.version_name += '_x'+str(self.parsed_filename['vendor_version']).zfill(2)
			
			self.parsed_filename['version_name'] = self.version_name	
		else :
			self.parsed_filename['version_name'] = self.temp_version_name
		
		return(self.version_name)



	def parseProject(self,wba_projects,file_name):

# 	Returns a tuple of (ProjectName,EpisodeName,Type)
# 	ProjectName and EpisideName are are passed in string format. None if they do not exist.
# 	Type is passed as either Shot,Asset or None in string format.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	wba_projects			dict				Dictionary of All WBA Project Configurations
# 	file_name				str					File name
# 	

		self.wba_projects = wba_projects
		self.file_name = file_name
		self.project_code = ''
			
		if self.debug : print " PARSING PROJECT/EPISODE:",file_name
		
		self.parsed_filename = {}
		
	# Split into Tokens
	
		try:
			self.all_tokens = self.file_name.split('_')
		except :
			pass
			self.parsed_filename['errors'].append('Cannot split filename into Tokens')
		
		#	Normal CG Shot     LGDC208_A01_1010_     LGDC208_001_1010_
		if re.match('^[A-Z]{4}[0-9]{3}_[A-Z]{1}[0-9]{2}_[0-9]{4}_',self.file_name) or re.match('^[A-Z]{4}[0-9]{3}_[0-9]{3}_[0-9]{4}_',self.file_name) is not None:			 
			self.parsed_filename['episode_name'] = self.all_tokens[0]
			self.parsed_filename['type'] = 'Shot'
			self.project_code = self.parsed_filename['episode_name'][:4]
		
		#	WBA DDR Shot       A01_1010_LGDC208_     001_1010_LGDC208_
		elif re.match('^[A-Z]{1}[0-9]{2}_[0-9]{4}_[A-Z]{4}[0-9]{3}_',self.file_name) or re.match('^[0-9]{3}_[0-9]{4}_[A-Z]{4}[0-9]{3}_',self.file_name) is not None:			
			self.parsed_filename['episode_name'] = self.all_tokens[2]
			self.parsed_filename['type'] = 'Shot'
			self.project_code = self.parsed_filename['episode_name'][:4]

		#	Old CG  Shot 	2-char Project Codes     LD194_A01_1010_
		if re.match('^[A-Z]{2}[0-9]{3}_[A-Z]{1}[0-9]{2}_[0-9]{4}_',self.file_name) is not None:			 
			self.parsed_filename['episode_name'] = self.all_tokens[0]
			self.parsed_filename['type'] = 'Shot'
			self.project_code = self.parsed_filename['episode_name'][:2]
				
		else :		# Not A Shot			
				
			#   Episode based Asset		LGDC208_
			if re.match('^[A-Z]{4}[0-9]{3}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['episode_name'] = self.all_tokens[0]
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.parsed_filename['episode_name'][:4]
			
			#   Project based Asset		LGDC_
			elif re.match('^[A-Z]{4}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				try:
					self.project_code = self.all_tokens[0]
				except:
					self.project_code = ''

			#   OLD Episode based Asset		LD194_
			elif re.match('^[A-Z]{2}[0-9]{3}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['episode_name'] = self.all_tokens[0]
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.all_tokens[0][:2]
				
			#   OLD Project based Asset		LD_
			elif re.match('^[A-Z]{2}_',self.file_name) is not None:
				self.parsed_filename['type'] = 'Asset'
				self.parsed_filename['asset_name'] = self.all_tokens[1]
				self.project_code = self.all_tokens[0][:2]
			
		if self.project_code != "" :						# Set Project	
			for self.wba_project_name in self.wba_projects.keys() :
				if 'wba_project_code' in self.wba_projects[self.wba_project_name] :				
					if  self.project_code == self.wba_projects[self.wba_project_name]['wba_project_code'] :
						self.parsed_filename['project_name'] = self.wba_project_name

		if 'project_name' in self.parsed_filename :
			if 'episode_name' in self.parsed_filename :		# Set Episode
				if self.debug :  print "  FOUND PROJECT: %s EPSIDOE: %s" % (self.parsed_filename['project_name'],self.parsed_filename['episode_name'])			
				return (self.parsed_filename['project_name'],self.parsed_filename['episode_name'],self.parsed_filename['type'])
			else :
				if self.debug :  print "  FOUND PROJECT: %s" % (self.parsed_filename['project_name'],self.parsed_filename['type'])
				return (self.parsed_filename['project_name'],'None',self.parsed_filename['type'])
		else:
			return ('None','None','None')		


	def projectExits(self,project_name):

# 	Return Project {object} if Project exists.
# 	Return None if Project does not exist.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	project_name				str				Project name
# 	

	
		self.project_name = project_name
		
		self.sg_project = self.sg.find_one("Project", [["name","is", self.project_name ]],['name'])

		if self.sg_project is None:			
			return False
		else :
			return (self.sg_project)


	def episodeExists(self,project_name,episode_name):

# 	Return Episode {object} if Published File exists.
# 	Return None if Episode does not exist.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	project_name				str				Project name
# 	episode_name				str				Episode name
# 	

		self.project_name = project_name
		self.episode_name = episode_name

		self.sg_project = self.sg.find_one("Project", [["name","is", self.project_name ]],['name'])
		self.sg_episode = self.sg.find_one('CustomEntity01', [['project','is',self.sg_project],["code","is", self.episode_name ]],['id','code'])		

		if self.sg_episode is None:			
			return False
		else :
			return (self.sg_episode)


	def assetExists(self,sg_project,asset_name,type):

# 	Return Asset {object} if Asset exists.
# 	Return None if Asset does not exist.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	sg_project				{object}		Shotgun Project object
# 	asset_name				str				Asset name
# 	type					str				Asset type
# 	

		self.sg_project = sg_project
		self.asset_name = asset_name
		self.type = type
		
		if self.type == "Act" : 
			self.type = "CustomEntity02"      # this fixes the mismatch between the human name 'Act' and the Shotgun name 'CustomEntity02'
		
		filters = [ ['project','is', self.sg_project],
					['code', 'is', self.asset_name] ]
		self.sg_asset = self.sg.find_one(self.type,filters,['code','sg_asset_type'])

		if self.sg_asset is None:			
			return False
		else :
			return (self.sg_asset)
			

	def versionExists(self,sg_project,version_name):					# Update this...

# 	Return Version {object} if Version exists.
# 	Return None if Version does not exist.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	sg_project				{object}		Shotgun object of current Project
# 	version_name			str				Version name
# 	

		self.sg_project = sg_project
		self.version_name = version_name
						
		filters = [ ['project','is', self.sg_project],
					['code', 'is', self.version_name] ]
		self.sg_version = self.sg.find_one('Version',filters,['code'])

		if self.sg_version is None:		
			return False
		else :
			return (self.sg_version)

			
	def	publishedFileExists(self,pub_file_name):

# 	Return PublishedFile {object} if Published File exists.
# 	Return None if Published File does not exist.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	pub_file_name				str				Published File name 'code'
# 

		self.pub_file_name = pub_file_name
		
		filters = [ ['code', 'is', self.pub_file_name] ]
		self.sg_published_file = self.sg.find_one('PublishedFile',filters,['code','version','path'])

		if self.sg_published_file is None:		
			return False
		else :
			return (self.sg_published_file)
		

	def assetType(self,asset_name,project_name):				# Make this the new new...

# 	Return the Asset Type {object] if Asset exists.
# 	Return None if Asset does not exist or has no 'sg_asset_type'
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	asset_name			str				Asset name to get Type
# 	project_name		str				Current Project name
# 

		self.asset_name = asset_name
		self.project_name = project_name
		self.sg_project = self.sg.find_one("Project", [["name","is", self.project_name ]],['name'])
		
		self.sg_project = self.sg.find_one("Project", [["name","is", self.project_name ]],['name'])							
		filters = [ ['project','is', self.sg_project],['code', 'is', self.asset_name] ]							 					 
		
		try:
			self.sg_asset = self.sg.find_one("Asset",filters,['sg_asset_type'])
			if self.sg_asset != None :
				if 'sg_asset_type' in self.sg_asset:
					return (self.sg_asset['sg_asset_type'])
			else :
				return None
		except:
			return None



	def scanDirectory(self, import_dir_path):

# 	Return the Asset Type {object] if Asset exists.
# 	Return None if Asset does not exist or has no 'sg_asset_type'
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	import_dir_path				str				Path of directory to scan
# 

		try:	
			import_path,import_dir_name = import_dir_path.rsplit('/',1)
		except:
			import_path = ''
			import_dir_name = import_dir_path

		if self.debug :
			print "--------------------------------------------------------------------------------"
			print "\n SCANNING DIRECTORY:",import_dir_path
	
		import_directory_files = []
		current_files = []
		found_files = []
		found_archives = []
		found_excel_docs = []
	
		for (current_dir, dir_names, filenames) in os.walk(import_dir_path):
			for filename in filenames:
				if not filename.startswith(('.','~')) :
					add_file = os.path.join(current_dir, filename)
					add_contents = add_file.split(import_dir_path)[1]
					current_files.append(add_contents)
					import_directory_files.append(add_file)
				
		for file_path in import_directory_files :																			
			if os.path.isfile(file_path):	
				try :
					file_path_extension = file_path.rsplit('.',1)[1]
			
					if file_path_extension.lower() in import_file_types :	
						if self.debug : print "  Found File:",file_path		
						found_files.append(file_path)

					if file_path_extension.lower() == 'zip' :	
						if self.debug : print "  Found Archive:",file_path	
						found_archives.append(file_path)
			
					if file_path_extension.lower() == 'xlsx' or file_path_extension.lower() == 'xls':	
						if self.debug : print "  Found Excel Document:",file_path	
						found_excel_docs.append(file_path)
				except :
					pass
			else :
				pass

	# Build return dictionary
	
		scanned_directory_dict = {
# 						'import_dir_name' = import_dir_name,
						'found_files' : found_files,
						'found_archives' : found_archives,
						'found_excel_docs' : found_excel_docs,
						'current_files' : current_files
						}

		return (scanned_directory_dict)
			
# 		return (import_dir_name,found_files,found_archives,found_excel_docs,current_files)			# remove import_dir_name


	def validateShotgun(self,sg_project,wba_projects,import_path):

# 	First, try to parse filename.
# 	If parsing fails return False.
# 		Only returns false if the 'version_name' could not be determined from parsing.
# 	If parsed 'asset_name' does not exist in Shotgun return 'asset_name' to build list of missing assets.
# 		Only returns strings for missing assets.
# 	If Asset exists the check that parsed Version exists in Shotgun.
# 	If Version Exists, return the Version {object} to build list of existing Versions.
# 	If Version does not exist, return the Asset {object} so we have the information.
# 	
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	sg_project				{object}		Shotgun object for current Project
# 	wba_projects			{dict}			WBA Project Configurations
# 	import_path				str				Filepath to validate
# 	
	
		self.sg_project = sg_project
		self.wba_projects = wba_projects
		self.import_path = import_path
	
		try:		
			self.import_path_dir,self.import_file_name = self.import_path.rsplit('/',1)
		except:
			self.import_path_dir = ''
			self.import_file_name = self.import_path
			
		if self.import_path_dir == '' :
			try:		
				self.import_path_dir,self.import_file_name = self.import_path.rsplit('/',1)
			except:
				self.import_path_dir = ''
				self.import_file_name = self.import_path

		self.parsed_version_dict = self.parseFilename(self.import_file_name,self.wba_projects)
		
		if 'task_name' not in self.parsed_version_dict :		
			return ('NoTask')			
							
		if 'version_name' in self.parsed_version_dict :
			self.version_name = self.parsed_version_dict['version_name']			
			
			if ('asset_name' in self.parsed_version_dict) & ('type' in self.parsed_version_dict) :
				self.asset_exists = self.assetExists(self.sg_project,self.parsed_version_dict['asset_name'],self.parsed_version_dict['type'])			# See is this Asset exists...			
								
				if self.asset_exists is False :    				 				
					return ((self.parsed_version_dict['asset_name'],self.parsed_version_dict['type']))									# Asset does not exist, return asset_name.
				
				else:
					self.version_exists = self.versionExists(self.sg_project,self.parsed_version_dict['version_name'])	# See if this Version exists...
										
					if self.version_exists is False :
						
						self.asset_exists.update({'new_version':self.parsed_version_dict['version_name']})
							   					
						return self.asset_exists								# Version does not exist, return Asset object.
					else:
						return self.version_exists							# If Version Exists, return Version object

		return (False)													# Could not parse Version, return False



	def wbaProjects(self) :
			
# 	Get the current Projects Configuration and Episodes from Shotgun
# 	Return a Dictionary of Project Configuration information
# 

		sg_projects = self.sg.find('Project',[['sg_type','in',('2D','3D')],['sg_status','is','Active']],['id','name','sg_type','sg_help_wiki_root','sg_project_vendor','sg_project_volume','sg_project_folder','sg_cg_volume','sg_cg_folder','sg_production_folder','sg_production_path','sg_local_media_path',
		'sg_task_tokens','sg_project_code'])
		
		wba_projects = {}

		for sg_project in sg_projects :
			sg_episodes = self.sg.find('CustomEntity01',[['project','is',sg_project],['sg_status_list','is','ip']],['id','code'])			
			episodes_all = []
			for sg_episode in sg_episodes :
				episodes_all.append(sg_episode['code'])
			project_task_tokens = {}			
			if sg_project['sg_task_tokens'] :
				split_task_tokens = sg_project['sg_task_tokens'].split(',')
				for token_task in split_task_tokens :
					token_task = token_task.rstrip().lstrip()					
					if token_task != "" and ':' in token_task:
						try :
							token,task = token_task.split(':')	
							project_task_tokens.update({token:task})
						except :
							pass
			
			wba_projects.update({sg_project['name']:{
			'wba_help_wiki_root':sg_project['sg_help_wiki_root'],
			'wba_project_type':sg_project['sg_type'],
			'wba_project_code':sg_project['sg_project_code'],
			'wba_episodes':tuple(episodes_all),
			'wba_project_volume':sg_project['sg_project_volume'],
			'wba_project_folder':sg_project['sg_project_folder'],
			'wba_cg_volume':sg_project['sg_cg_volume'],
			'wba_cg_folder':sg_project['sg_cg_folder'],
			'wba_production_folder':sg_project['sg_production_folder'],
			'wba_production_path':sg_project['sg_production_path'],
			'wba_local_media_path':sg_project['sg_local_media_path'],
			'wba_task_tokens':project_task_tokens
			}})
			
			if sg_project['sg_project_vendor'] != None :
				if 'name' in sg_project['sg_project_vendor'] :
					wba_projects[sg_project['name']]['wba_project_vendor'] = sg_project['sg_project_vendor']['name']

				else :
					wba_projects[sg_project['name']]['wba_project_vendor'] = ''
									
		wba_projects_cleaned = {}
		
		for iterate_project,uncleaned_dict in wba_projects.iteritems() :
		
			cleaned_dict = dict((k, v) for k, v in uncleaned_dict.iteritems() if v is not None)			
			wba_projects_cleaned.update({iterate_project:cleaned_dict})
		
		if self.debug :

			print "\n\nShotgun Project Configuration Information..."
			print "--------------------------------------------------------------------------------"
			print "wba_projects2 :",wba_projects_cleaned
			print "--------------------------------------------------------------------------------"
				
		return (wba_projects_cleaned)




#############################################################################################




class startupSplash(QtGui.QDialog):

# 	A generic application-loading splash screen QDialog
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	app_name			str		Name of Application for splash
# 	software_version	str		Application verions
# 

	progressTextSignal = QtCore.Signal(str,str)
	setProgressSignal = QtCore.Signal(int)
	  
	def __init__(self, app_name, software_version, parent=None):
		super(startupSplash, self).__init__(parent)
		
		global splash_steps
		
		self.app_name = app_name
		self.software_version = software_version

		
	# Connect signals to the main thread.
	
		self.progressTextSignal.connect(self.setStartupSplashText)
		self.setProgressSignal.connect(self.setStartupSplash)

	# Set colors
	
		gui_bg_color = QtGui.QColor(50,50,50)
		normal_font = QtGui.QFont()
		normal_font.setPointSize(10)		# Font for Splash Message
		small_font = QtGui.QFont()
		small_font.setPointSize(9)		    # Font for Splash Lower Message
		big_font = QtGui.QFont() 
		big_font.setPointSize(18)		    # Font for Splash App Name
		white_text = QtGui.QPalette()
		white_text.setColor(QtGui.QPalette.Foreground,QtCore.Qt.white)
		ltblue_text = QtGui.QPalette()
		ltblue_text.setColor(QtGui.QPalette.Foreground,QtGui.QColor(60,160,250))
	
		self.setWindowTitle("Loading...")
		self.setPalette(QtGui.QPalette(gui_bg_color))
		self.setAutoFillBackground(True)				
		self.setFixedWidth(300)
		self.setFixedHeight(160)

		self.splash_app_name = QtGui.QLabel(self.app_name)
		self.splash_app_name.setAlignment(QtCore.Qt.AlignCenter)
		self.splash_app_name.setFont(big_font)
		self.splash_app_name.setPalette(white_text)
		self.splash_app_version = QtGui.QLabel(self.software_version)
		self.splash_app_version.setAlignment(QtCore.Qt.AlignCenter)
		self.splash_app_version.setFont(normal_font)
		self.splash_app_version.setPalette(ltblue_text)
		
# 		self.splash_app_box = QtGui.QHBoxLayout()
# 		self.splash_app_box.addWidget(self.splash_app_name)
# 		self.splash_app_box.addStretch(1)
# 		self.splash_app_box.addWidget(self.splash_app_version)
		
		self.splash_copyright_info = QtGui.QLabel("Copyright 2018 All Rights Reserved\n\nDaniel R. Eaton, Warner Bros. Animation")
		self.splash_copyright_info.setAlignment(QtCore.Qt.AlignCenter)
		self.splash_copyright_info.setFont(small_font)
		self.splash_copyright_info.setPalette(white_text)
		self.space1 = QtGui.QLabel("")
		self.space1.setFixedHeight(10)	
		self.splash_message = QtGui.QLabel('initializing...')
		self.splash_message.setAlignment(QtCore.Qt.AlignLeft)
		self.splash_message.setFont(normal_font)
		self.splash_message.setPalette(white_text)
		self.splash_progress_bar = QtGui.QProgressBar()
		self.splash_progress_bar.setAlignment(QtCore.Qt.AlignCenter)
		self.splash_message_lower = QtGui.QLabel('')
		self.splash_message_lower.setAlignment(QtCore.Qt.AlignLeft)
		self.splash_message_lower.setFont(small_font)
		self.splash_message_lower.setPalette(white_text)
# 		self.splash_message_lower.setFixedHeight(190)
		
		self.splash_progress_box = QtGui.QVBoxLayout()
		self.splash_progress_box.setContentsMargins(0,0,0,0)
		self.splash_progress_box.setSpacing(4)
		self.splash_progress_box.addWidget(self.splash_app_name)
		self.splash_progress_box.addWidget(self.splash_app_version)
 		self.splash_progress_box.addStretch(1)
		self.splash_progress_box.addWidget(self.splash_copyright_info)
		self.splash_progress_box.addWidget(self.space1)
		self.splash_progress_box.addWidget(self.splash_message)
		self.splash_progress_box.addWidget(self.splash_progress_bar)
		self.splash_progress_box.addWidget(self.splash_message_lower)
		
# 		self.splash_message_lower.setVisible(False)				# Hide lower message 

		self.splash_main_box = QtGui.QVBoxLayout()
		self.splash_main_box.setContentsMargins(10,10,10,10)
		self.splash_main_box.setSpacing(10)
# 		self.splash_main_box.addLayout(self.splash_app_box)
		self.splash_main_box.addLayout(self.splash_progress_box)	
	
		self.setLayout(self.splash_main_box)
		self.setWindowFlags( QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint )		# No Window Title Bar

		QtGui.QApplication.processEvents()
		
		self.show()
		self.raise_()


	def setStartupSplashMaximum(self, value):
		if hasattr(self, 'splash_progress_bar'):
			self.splash_progress_bar.setMaximum(value)
			
			QtGui.QApplication.processEvents()

	
	def setStartupSplashText(self, splash_message, splash_message_lower):
		self.splash_message.setText(splash_message)
		self.splash_message_lower.setText(splash_message_lower)
				
		QtGui.QApplication.processEvents()

		
	def setStartupSplash(self, value):
		self.splash_progress_bar.setValue(value)
		
		QtGui.QApplication.processEvents()



#############################################################################################



class wbaShotgunLogin(QtGui.QDialog):

# 	A Shotgun specific login screen QDialog
# 	---------------------------------------------------------------
# 	Inputs
# 	
# 	current_user	str					Name of Application for splash
# 	sg				{object}			Current Shotgun instance from Application
# 	debug			boolean				Debug flag
# 
	   
    def __init__(self, current_user, sg, debug, parent=None):
		super(wbaShotgunLogin, self).__init__(parent)
		
		self.sg = sg
		self.current_user = current_user
		self.debug = debug
		
	# Get current_user password from Keychain
	
		import keyring.backends.kwallet
 		import keyring.backends.OS_X
 		import keyring.backends.SecretService
 		import keyring.backends.Windows
		import keyring

		try: self.keyring_password = keyring.get_password(keyring_servicename, current_user)
		except: self.keyring_password = ''
		

	# Set colors
	
		gui_bg_color = QtGui.QColor(50,50,50)
		normal_font = QtGui.QFont()
		normal_font.setPointSize(10)		# Font for Splash Message
		small_font = QtGui.QFont()
		small_font.setPointSize(9)		    # Font for Splash Lower Message
		big_font = QtGui.QFont() 
		big_font.setPointSize(18)		    # Font for Splash App Name
		white_text = QtGui.QPalette()
		white_text.setColor(QtGui.QPalette.Foreground,QtCore.Qt.white)
		ltblue_text = QtGui.QPalette()
		ltblue_text.setColor(QtGui.QPalette.Foreground,QtGui.QColor(60,160,250))
			
	# Find Icons

		self.wba_logo = 'wba_logo_blue_vsmall_badge.png'		
		if "/Applications/ShotgunAMIEngine.app/Contents/" in os.path.realpath(__file__) :
			self.icon_dir = os.path.join(os.sep+'Applications','ShotgunAMIEngine.app','Contents','Resources','WBA_Tools','icons')	
		elif "/Applications/" in os.path.realpath(__file__) :
			self.icon_path_split = os.path.realpath(__file__).split('/')
			self.icon_dir = os.path.join(os.sep+self.icon_path_split[0],self.icon_path_split[1],'Contents','Resources','WBA_Tools','icons')
		else:
		 	self.icon_dir = os.path.join(os.sep+'Applications','ShotgunAMIEngine.app','Contents','Resources','WBA_Tools','icons')
		self.wba_logo_path = os.path.join(self.icon_dir,self.wba_logo)
					
		self.setMinimumWidth(400)
		self.setMaximumWidth(600)
		self.setFixedHeight(190)
		
		self.wba_title = QtGui.QLabel("WBA Shotgun Login")
		self.wba_title.setFont(big_font)
		self.wba_title.setPalette(white_text)
		self.wba_title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		self.wba_title_message = QtGui.QLabel("Please login with your Shotgun Username and Password.")
		self.wba_title_message.setFont(normal_font)
		self.wba_title_message.setPalette(white_text)
		self.wba_title_message.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)		
		self.title_box = QtGui.QVBoxLayout()
		self.title_box.addWidget(self.wba_title)
		self.title_box.addWidget(self.wba_title_message)
		self.wba_icon_pixmap = QtGui.QPixmap(self.wba_logo_path)
		self.wba_icon = QtGui.QLabel(self)
		self.wba_icon.setPixmap(self.wba_icon_pixmap)
		self.wba_icon.setAlignment(QtCore.Qt.AlignLeft)		
		self.top_box =  QtGui.QHBoxLayout()
		self.top_box.addWidget(self.wba_icon)
		self.top_box.addLayout(self.title_box)
		self.top_box.addStretch()

		self.username_label = QtGui.QLabel("Username:")
		self.username_label.setFixedWidth(60)
		self.username_label.setFont(normal_font)
		self.username_label.setPalette(white_text)
		self.username = QtGui.QLineEdit(current_user)
		self.username.setFont(normal_font)
		self.username.setPalette(white_text)
		self.username_box = QtGui.QHBoxLayout()
		self.username_box.addWidget(self.username_label)
		self.username_box.addWidget(self.username)

		self.password_label = QtGui.QLabel("Password:")
		self.password_label.setFixedWidth(60)
		self.password_label.setFont(normal_font)
		self.password_label.setPalette(white_text)
		self.password = QtGui.QLineEdit(self.keyring_password)
		self.password.setFont(normal_font)
		self.password.setPalette(white_text)
		self.password.setEchoMode(QtGui.QLineEdit.EchoMode.Password)
		self.password_box = QtGui.QHBoxLayout()
		self.password_box.addWidget(self.password_label)
		self.password_box.addWidget(self.password)

		self.save_password = QtGui.QCheckBox("    Save Password in Keychain")
		self.save_password.setFont(normal_font)
		self.save_password.setPalette(white_text)

		self.login_button = QtGui.QPushButton('Login', self)
		self.login_button.clicked.connect(lambda: self.handleLogin())
		self.login_button.setFont(normal_font)
		self.login_button.setFixedWidth(100)

		self.button_box = QtGui.QHBoxLayout()
		self.button_box.addWidget(self.save_password)
		self.button_box.addStretch()
		self.button_box.addWidget(self.login_button)

		self.main_box = QtGui.QVBoxLayout(self)   ## loose (self)???
		self.main_box.setSpacing(6)
		self.main_box.addLayout(self.top_box)
		self.main_box.addLayout(self.username_box)
		self.main_box.addLayout(self.password_box)
		self.main_box.addLayout(self.button_box)
	   
		self.setPalette(QtGui.QPalette(gui_bg_color))

		self.save_password.setChecked(True)

		self.show()
		self.raise_()


    def handleLogin(self):
    
    	self.login_username = self.username.text()
    	self.login_password = self.password.text()
    	
    	import keyring
    	
    	global current_user
    	
    	if self.authShotgunUser(self.login_username,self.login_password) :
          
			if self.debug : print " AUTHENTICATED : ",self.login_username

			if self.save_password.isChecked() :
				keyring.set_password(keyring_servicename, self.login_username, self.login_password)

			current_user = self.login_username
			self.accept()

        else:
            QtGui.QMessageBox.warning(
                self, 'Error', 'WARNING!\n\nSHOTGUN AUTHENTICATION FAILED!\n\nBad Username or Password')

               
    def authShotgunUser(self,login_username,login_password):
    
		self.login_username = login_username
		self.login_password = login_password
		
		self.auth = False
		
		try : self.auth = self.sg.authenticate_human_user(self.login_username, self.login_password, None)
		except: pass
			
		if self.auth != None : 
			return True
		else :
			return False


# This function is only so a symlink to this module can exist in the shotgunEventsDaemon plugins directory.
# Without it the Daemon will crash when it tries to load all the plugins.
# It never needs to run this module as a shotgunEventDaemon plugin, but this function must exist or there will be issues...
	
def registerCallbacks(reg):
	matchEvents = {
		'Shotgun_Version_New': None,
	}
