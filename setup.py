#!/usr/bin/env python
from setuptools import setup
def main():
	setup(
		name='html_parser',
		version=0.1,
		description='parse html as data tree',
		packages=['html_parser'],
		author='meh'
	)
if __name__ == '__main__':
	main()