################################################################################
###                                 Imports                                  ###
################################################################################
import os
from datetime import datetime
import shutil

################################################################################
###                                Class Def                                 ###
################################################################################
class Crust:
	"""
	Custom shell/terminal
	"""
	############################################################################
	def __init__(self, fin, fout, ferr):
		"""
		PURPOSE: creates a new Custom_Shell
		ARGS:
			fin (file-like object): where input is being read from
			fout (file-like object): where output is being written to
			ferr (file-like object): where error output is being written to
		RETURNS: new instance of a Custom_Shell
		NOTES:
		"""
		#Save arguments
		self.fin = fin
		self.fout = fout
		self.ferr = ferr

		#Define properties
		self.keep_going = False

	############################################################################
	def write_out_and_flush(self, out_str):
		"""
		PURPOSE: writes to fout and flushes the buffer
		ARGS:
			out_str (str): string to output
		RETURNS: none
		NOTES:
		"""
		self.fout.write(out_str)
		self.fout.flush()

	############################################################################
	def write_err_and_flush(self, out_str):
		"""
		PURPOSE: writes to ferr and flushes the buffer
		ARGS:
			out_str (str): string to output
		RETURNS: none
		NOTES:
		"""
		self.ferr.write(out_str)
		self.ferr.flush()

	############################################################################
	def parse_input(self, user_input):
		"""
		PURPOSE: parses the raw string of user input. Splits multiple commands 
			up and tokenizes each command
		ARGS:
			user_input (str): user input str
		RETURNS: (list) list of commands, where each command is a list of 
			strings representing command and argument
		NOTES:
		"""
		#Strip whitespace
		user_input = user_input.strip()

		#Break multi-command line into multiple commands
		user_input_list = user_input.split(';')
		if len(user_input_list) > 1:
			#Multi command so feed each command to this function recursively 
			#and save results in a list
			cmds = []
			for cur_input in user_input_list:
				cur_output = self.parse_input(cur_input)
				cmds.append(cur_output[0])
			return cmds
		else:
			#Single command so ignore list
			pass

		#Break command into command plus individual arguments
		cmd = user_input.split()

		#Return list of commands
		return [cmd]

	############################################################################
	def run(self):
		"""
		PURPOSE: main loop of the shell that waits for input, does something, 
			and then gives you the output
		ARGS:
		RETURNS: none
		NOTES:
		"""
		self.keep_going = True

		while self.keep_going:
			#Wait for user input
			dir_to_show = os.path.basename(os.getcwd())
			self.write_out_and_flush("(crust) %s>" % dir_to_show)
			#self.write_out_and_flush(">>>")
			user_input = self.fin.readline()

			#Parse user input
			cmds = self.parse_input(user_input)

			#Execute user input
			for cmd in cmds:
				if len(cmd) >= 1:
					actual_cmd = cmd[0]
					cmd_args = cmd[1:]

					#Switch on cmd
					try:
						if actual_cmd == "exit":
							self.keep_going = False
							break
						elif actual_cmd == "pwd":
							self.cmd_pwd(cmd_args)
						elif actual_cmd == "cd":
							self.cmd_cd(cmd_args)
						elif actual_cmd == 'ls':
							self.cmd_ls(cmd_args)
						elif actual_cmd == 'cp':
							self.cmd_cp(cmd_args)
						elif actual_cmd == 'cat':
							self.cmd_cat(cmd_args)
						elif actual_cmd == 'mv':
							self.cmd_mv(cmd_args)
						elif actual_cmd == 'mkdir':
							self.cmd_mkdir(cmd_args)
						elif actual_cmd == 'rmdir':
							self.cmd_rmdir(cmd_args)
						elif actual_cmd == 'rm':
							self.cmd_rm(cmd_args)
						elif actual_cmd == 'touch':
							self.cmd_touch(cmd_args)
						elif actual_cmd == 'locate':
							self.cmd_locate(cmd_args)
						else:
							err_msg = "%s: command not found\n" % actual_cmd
							self.write_err_and_flush(err_msg)
					except Exception as e:
						self.write_err_and_flush("Unknown error occurred: %s\n" % type(e))
						self.write_err_and_flush(str(e))

	############################################################################
	def cmd_pwd(self, cmd_args=[]):
		"""
		PURPOSE: executes 'pwd' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		cwd = os.getcwd() + "\n"
		self.write_out_and_flush(cwd)

	############################################################################
	def cmd_cd(self, cmd_args=[]):
		"""
		PURPOSE: executes 'cd' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given so find home directory and go there
			cd_arg = os.path.expanduser('~')
		else:
			cd_arg = cmd_args[0]

		try:
			os.chdir(cd_arg)
		except FileNotFoundError as e:
			self.write_err_and_flush("cd: %s: No such file or directory\n" % cd_arg)

	############################################################################
	def cmd_ls(self, cmd_args=[]):
		"""
		PURPOSE: executes 'ls' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		show_hidden_files = False
		long_listing = False
		human_readable = False

		#Find args that start with dash
		path_arg = ""
		dash_args = []
		for cur_arg in cmd_args:
			if cur_arg.startswith("-"):
				dash_args.append(cur_arg)
			elif path_arg == "":
				path_arg = cur_arg

		#Interpet modifiers (args that start with dash)
		for dash_arg in dash_args:
			if dash_arg.startswith("--"):
				cur_arg = dash_arg[2:]
				if cur_arg == "all":
					show_hidden_files = True
				else:
					self.write_err_and_flush("ls: unknown option --%s\n" % cur_arg)
					return
			else:
				cur_arg = dash_arg[1:]
				#Split into single letters
				for cur_letter in cur_arg:
					if cur_letter == 'a':
						show_hidden_files = True
					elif cur_letter == 'l':
						long_listing = True
					elif cur_letter == 'h':
						human_readable = True
					else:
						self.write_err_and_flush("ls: unknown option -%s\n" % cur_letter)
						return

		if path_arg == "":
			#No path argument was given so use current directory
			file_list = os.listdir()
		else:
			#Path argument was given
			try:
				file_list = os.listdir(path_arg)
			except FileNotFoundError as e:
				self.write_err_and_flush("ls: %s: No such directory\n" % path_arg)

		#Show or hide hidden files
		valid_file_list = []
		if show_hidden_files:
			valid_file_list = file_list
		else:
			for cur_file in file_list:
				if not cur_file.startswith('.'):
					valid_file_list.append(cur_file)

		#Long listing format
		if long_listing:
			ret_list = [['Permissions', 'Num Links', 'Owner ID', 'Group ID', 'Bytes', 'Modification Date', 'File']]
			for cur_file in valid_file_list:
				if path_arg:
					file_path = os.path.join(path_arg, cur_file)
				else:
					file_path = os.path.join(os.getcwd(), cur_file)
				cur_ret_list = []
				is_dir = False
				if os.path.isdir(file_path):
					is_dir = True
					permission_str = 'd'
				else:
					permission_str = '-'

				stat_res = os.stat(file_path)
				stat_mode = stat_res[0]
				reverse_perm_str = ""
				for ii in range(3):
					if (stat_mode & 1):
						reverse_perm_str = 'x' + reverse_perm_str
					else:
						reverse_perm_str = '-' + reverse_perm_str
					stat_mode = stat_mode >> 1
					if (stat_mode & 1):
						reverse_perm_str = 'w' + reverse_perm_str
					else:
						reverse_perm_str = '-' + reverse_perm_str
					stat_mode = stat_mode >> 1
					if (stat_mode & 1):
						reverse_perm_str = 'r' + reverse_perm_str
					else:
						reverse_perm_str = '-' + reverse_perm_str
					stat_mode = stat_mode >> 1
				permission_str += reverse_perm_str
				cur_ret_list.append(permission_str)

				#TODO if linux look up user and group id for 4 and 5
				cur_ret_list.append(str(stat_res[3]))
				cur_ret_list.append(str(stat_res[4]))
				cur_ret_list.append(str(stat_res[5]))
				file_size = stat_res[6]
				if human_readable:
					for unit in ["", "K", "M", "G", "T"]:
						if abs(file_size) < 1024.0:
							file_size = "%.1f%s" % (file_size, unit)
							break
						file_size /= 1024.0
				cur_ret_list.append(str(file_size))
				file_date = datetime.fromtimestamp(stat_res[8]).strftime("%b %d %H:%M")
				cur_ret_list.append(file_date)
				cur_ret_list.append(cur_file)

				ret_list.append(cur_ret_list)

			col0_len = 0
			col1_len = 0
			col2_len = 0
			col3_len = 0
			col4_len = 0
			col5_len = 0
			for col in range(6):
				max_len = 0
				for row in range(len(ret_list)):
					cur_len = len(ret_list[row][col])
					if cur_len > max_len:
						max_len = cur_len
				for row in range(len(ret_list)):
					cur_len = len(ret_list[row][col])
					to_add = max_len - cur_len
					if to_add >= 1:
						ret_list[row][col] += ' ' * to_add

			ret_str = ""
			for cur_row in ret_list:
				ret_str += " ".join(cur_row) + "\n"
		else:
			ret_str = " ".join(valid_file_list) + "\n"
		self.write_out_and_flush(ret_str)

	############################################################################
	def cmd_cp(self, cmd_args=[]):
		"""
		PURPOSE: executes 'cp' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 2:
			#No arguments were given
			self.write_err_and_flush("cp: requires at least 2 arguments\n")
			return
		elif len(cmd_args) == 2:
			#Check for directory
			if os.path.isdir(cmd_args[0]):
				self.write_err_and_flush("cp: '%s' cannot be a directory\n")
				return
			if os.path.isdir(cmd_args[1]):
				basename = os.path.basename(cmd_args[0])
				cmd_args[1] = os.path.join(cmd_args[1], basename)

			try:
				shutil.copyfile(cmd_args[0], cmd_args[1])
			except shutil.SameFileError as e:
				self.write_err_and_flush("cp: '%s' and '%s' are the same file\n" % (cmd_args[0], cmd_args[1]))
			except PermissionError as e:
				self.write_err_and_flush("cp: Permission denied\n")
			except FileNotFoundError as e:
				self.write_err_and_flush("cp: No such file or directory\n")
		else:
			#Should be multiple files copying into a directory
			for ii in range(len(cmd_args) - 1):
				if not os.path.isfile(cmd_args[ii]):
					self.write_err_and_flush("cp: '%s' needs to be a file\n" % cmd_args[ii])
					return
			if not os.path.isdir(cmd_args[-1]):
				self.write_err_and_flush("cp: '%s' needs to be a directory\n" % cmd_args[-1])
			for ii in range(len(cmd_args) - 1):
				shutil.copyfile(cmd_args[ii], os.path.join(cmd_args[-1], os.path.basename(cmd_args[ii])))

	############################################################################
	def cmd_cat(self, cmd_args=[]):
		"""
		PURPOSE: executes 'cat' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if not cmd_args:
			#No arguments given
			self.write_err_and_flush("cat: requires at least 1 argument\n")
			return

		cat_str = ""
		file_to_write_to = ""
		overwrite_file = False
		for ii in range(len(cmd_args)):
			cur_arg = cmd_args[ii]
			if cur_arg == ">":
				if len(cmd_args) == (ii + 1):
					self.write_err_and_flush("A target file is required with use of '>'\n")
					return
				file_to_write_to = cmd_args[ii + 1]
				overwrite_file = True
				break
			elif cur_arg == ">>":
				if len(cmd_args) == (ii + 1):
					self.write_err_and_flush("A target file is required with use of '>>'\n")
					return
				file_to_write_to = cmd_args[ii + 1]
				overwrite_file = False
				break
			else:
				try:
					cur_file = os.path.join(os.getcwd(), cur_arg)
					with open(cur_file, 'r') as fh:
						cat_str += fh.read()
				except FileNotFoundError as e:
					self.write_err_and_flush("Could not find file '%s'\n" % cur_arg)
					return

		if file_to_write_to:
			try:
				full_file_write_to = os.path.join(os.getcwd(), file_to_write_to)
				if overwrite_file:
					with open(full_file_write_to, 'w') as fh:
						fh.write(cat_str)
				else:
					with open(full_file_write_to, 'a') as fh:
						fh.write(cat_str)
			except Exception as e:
				self.write_err_and_flush("Could not write to file '%s'\n" % file_to_write_to)
				return
		else:
			self.write_out_and_flush(cat_str)

	############################################################################
	def cmd_mv(self, cmd_args=[]):
		"""
		PURPOSE: executes 'mv' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 2:
			#No arguments were given
			self.write_err_and_flush("mv: requires at least 2 arguments\n")
			return
		else:
			try:
				shutil.move(cmd_args[0], cmd_args[1])
			except shutil.SameFileError as e:
				self.write_err_and_flush("mv: '%s' and '%s' are the same file\n" % (cmd_args[0], cmd_args[1]))
			except PermissionError as e:
				self.write_err_and_flush("mv: Permission denied\n")
			except FileNotFoundError as e:
				self.write_err_and_flush("mv: No such file or directory\n")

	############################################################################
	def cmd_mkdir(self, cmd_args=[]):
		"""
		PURPOSE: executes 'mkdir' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given
			self.write_err_and_flush("mkdir: requires 1 argument\n")
			return
		try:
			os.makedirs(cmd_args[0])
		except Exception as e:
			self.write_err_and_flush("Could not make directory '%s'\n" % cmd_args[0])

	############################################################################
	def cmd_rmdir(self, cmd_args=[]):
		"""
		PURPOSE: executes 'rmdir' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given
			self.write_err_and_flush("rmdir: requires at least 1 argument\n")
			return
		for cur_arg in cmd_args:
			try:
				shutil.rmtree(cur_arg)
			except NotADirectoryError as e:
				self.write_err_and_flush("'%s' is not a directory\n" % cur_arg)
			except Exception as e:
				self.write_err_and_flush("Could not remove directory '%s'\n" % cur_arg)

	############################################################################
	def cmd_rm(self, cmd_args=[]):
		"""
		PURPOSE: executes 'rm' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given
			self.write_err_and_flush("rm: requires at least 1 argument\n")
			return
		for cur_arg in cmd_args:
			if os.path.isdir(cur_arg):
				self.cmd_rmdir([cur_arg])
			else:
				try:
					os.remove(cur_arg)
				except Exception as e:
					self.write_err_and_flush("Could not remove '%s'\n" % cur_arg)

	############################################################################
	def cmd_touch(self, cmd_args=[]):
		"""
		PURPOSE: executes 'touch' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given
			self.write_err_and_flush("touch: requires at least 1 argument\n")
			return

		for cur_arg in cmd_args:
			try:
				with open(cur_arg, 'a') as fh:
					pass
			except Exception as e:
				self.write_err_and_flush("Could not open file '%s'\n" % cur_arg)

	############################################################################
	def cmd_locate(self, cmd_args=[]):
		"""
		PURPOSE: executes 'locate' command
		ARGS:
			cmd_args (list): list of strings representing arguments
		RETURNS: none
		NOTES: may write to fout and ferr
		"""
		if len(cmd_args) < 1:
			#No arguments were given
			self.write_err_and_flush("locate: requires at least 1 argument\n")
			return
		file_to_find = cmd_args[0]

		files_found = ""
		home_dir = os.path.abspath('.').split(os.path.sep)[0] + os.sep
		for path, subdirs, files in os.walk(home_dir):
			for name in files:
				if file_to_find in name:
					file_path = os.path.join(path, name)
					files_found += file_path + "\n"
		if not files_found:
			self.write_err_and_flush("Could not find '%s'\n" % file_to_find)
		else:
			self.write_out_and_flush(files_found)

################################################################################
###                                  Main                                    ###
################################################################################
if __name__ == "__main__":
	import sys
	crust = Crust(sys.stdin, sys.stdout, sys.stderr)
	crust.run()

################################################################################
###                               End of File                                ###
################################################################################