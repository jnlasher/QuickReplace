#!/usr/bin/env python3
import os
import sys
import re
import fileinput
from argparse import ArgumentParser

HELP_TEXT      = "Value of the current text to replace"
HELP_REPLACE   = "Value of the new text to set"
HELP_DIRECTORY = "Optional directory to search in. Defaults to current directory if not provided"
HELP_RECURSIVE = "Find and replace recursively"
HELP_EXTENSION = "Limits changes to a given file extension. Default searches all file types."
HELP_VERBOSE   = "Output content before text replacement"
HELP_REGEX     = "Use pattern matching with regular expression instead of string literal in text_to_replace"

def initialize():
	"""
	Usage: 
		A simple find and replace script for editing files.
		Command line arguments can limit the scope and values
		to edit to.
		
	Args:
		-t, --current_text: The current text you wish to replace
		-n, --new_text: The new text you wish to replace it with
		-d, --directory: The base directory to start searching. If not given, will use the current working directory
		-r, --recursive: Flag to enable recursive find and replace
		-x, --extension: Limit the find and replace to only certain file types
	"""
	parser = ArgumentParser()
	parser.add_argument("text_to_replace",   help=HELP_TEXT)
	parser.add_argument("replacement_text",  help=HELP_REPLACE)
	parser.add_argument("-d", "--directory", help=HELP_DIRECTORY)
	parser.add_argument("-r", "--recursive", help=HELP_RECURSIVE, action="store_true")
	parser.add_argument("-x", "--extension", help=HELP_EXTENSION)
	parser.add_argument("-v", "--verbose",   help=HELP_VERBOSE,   action="store_true")
	parser.add_argument("-g", "--regex",     help=HELP_REGEX,     action="store_true")
	# TODO parser.add_argument("-b", "--backup", help="Creates a .bak file before replacing the text")
	# TODO parser.add_argument("-a", "--ask", help="Outputs the text to be replaced; Press 'y' to proceed with changes and 'n' to reject changes")

	args = parser.parse_args()
	return vars(args)


class QuickReplace:

	def __init__(self, **kwargs):
		self.text_to_replace = kwargs.get('text_to_replace')
		self.replacement_text = kwargs.get('replacement_text')
		self.recursive = kwargs.get('recursive', False)
		self.verbose = kwargs.get('verbose', False)
		self.extension = kwargs.get('extension', ".*")
		
		self.regex = kwargs.get('regex', False)
		print(self.regex)
		if self.regex:
			self.text_to_replace = re.compile(self.text_to_replace)
			self.REPLACE = self._replace_regex
		else:
			self.REPLACE = self._replace_text
			
		directory = kwargs.get('directory')
		if directory:
			self.directory = self._format_working_directory(directory)
		else:
			self.directory = os.getcwd()

	def run(self):
		if self.recursive:
			self._recursive_walkthrough()
		else:
			self._flat_walkthrough()

	def _recursive_walkthrough(self):
		for root, dirs, files in os.walk(self.directory):
			for name in files:
				if self.extension and not name.endswith(self.extension):
					continue
				self._replace_in_file(root, name)

	def _flat_walkthrough(self):
		for name in os.listdir(self.directory):
			if self.extension and not name.endswith(self.extension):
				continue
			self._replace_in_file(self.directory, name)
	
	def _replace_in_file(self, directory, name):
		abs_path = os.path.join(directory, name)
		with fileinput.FileInput(abs_path, inplace=True) as file:
			try:
				for line in file:
					print(self.REPLACE(line, self.text_to_replace, self.replacement_text), end="")
			except FileExistsError:
				continue
	
	@staticmethod
	def _replace_regex(line, text_in, text_out, **args):
		return text_in.sub(text_out, line)
	
	@staticmethod
	def _replace_text(line, text_in, text_out, **args):
		return line.replace(text_in, text_out)

	@staticmethod
	def _format_working_directory(directory_name):
		# TODO - Formatting for *nix systems
		return '\\'.join(directory_name.split('\\'))


if __name__ == '__main__':
	var_args = initialize()
	print(var_args)
	qr = QuickReplace(**var_args)
	qr.run()
