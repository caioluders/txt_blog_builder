#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import argparse
import functools
import datetime
import string
import operator
import json
import re
import markdown


def parse_file(file):
		try:
			f = open(file, "r").read().splitlines()
			return {"title": f[0], "date": f[1]}
		except:
			return {"title": "", "date": ""}


def parse_markdown(file , template, cfg) :
		f = open(file, "r").read()

		template_style = re.search("<style>(.*)</style>", template , re.MULTILINE |
		re.DOTALL).group(1)

		html = """<!DOCTYPE html>
<html>
<style>
%s
</style>
<head>
  <meta charset="UTF-8">
</head>

<body>""" % (template_style)

		html += markdown.markdown(f, extensions=['fenced_code'])
		html += "</body><hr>%s</html>" % (cfg["footnote"])
		return html

def make_index(root, dirs, files, cfg):
		path = os.path.abspath(root)

		template = open(cfg["theme"], "r").read()

		table_html = ""

		print(path)

		table_html += """<tr>
	<td><a href="../">../</a></td>
	<td></td>
	<td></td>
</tr>
"""

		for d in dirs:
				table_html += """<tr>
	<td><a href="%s">%s</a></td>
	<td>%s</td>
	<td>%s</td>
</tr>
""" % (d, d, "Directory", "-")

		files_dated = []

		for f in files:
				metadata = parse_file(os.path.join(path, f))
				if f[-3:] == ".md" :
					html_md = parse_markdown(os.path.join(path,f), template ,
					cfg)
					fw = open(os.path.join(path,f[:-3]+".html"),"w")
					fw.write(html_md)
					try :
						files_dated.remove([f[:-3]+".html","<!DOCTYPE html>","<html>"])
					except :
						pass
					files_dated.append([f[:-3]+".html", metadata["title"], metadata["date"]])
					continue
				_file_metadata  = [f, metadata["title"], metadata["date"]]
				if not any( _file_metadata[0] in fff for fff in files_dated ) : 
					files_dated.append(_file_metadata)

		files_dated = sorted(files_dated, key=operator.itemgetter(2), reverse=True)

		for f in files_dated:
				table_html += """<tr>
	<td><a href="%s">%s</a></td>
	<td>%s</td>
	<td>%s</td>
</tr>
""" % (f[0], f[0], f[1], (datetime.datetime.fromtimestamp(int(
						f[2])).strftime("%d/%m/%Y") if f[2].isdigit() else f[2]))
		
		html_result = string.Template(template).substitute({
				"posts_table":
				table_html,
				"blog_title":
				cfg["title"],
				"footnote":
				cfg["footnote"]
		})

		index_file = open(os.path.join(path, "index.html"), "w", encoding="utf-8")
		index_file.write(html_result)
		index_file.close()


def main(args):

		path = os.path.abspath(args.path)

		config = json.loads(open(args.config).read())

		for root, dirs, files in os.walk(path):
				files = [
						f for f in files if not f[0] == '.' and f not in config["ignore"]
				]
				dirs[:] = [d for d in dirs
									 if not d[0] == '.']	# ignore hidden files/dirs

				make_index(os.path.join(path, root), dirs, files, config)


if __name__ == "__main__":
		parser = argparse.ArgumentParser(
				description="Create a blog from .txt files")
		parser.add_argument('-p', '--path', help="Path of the files.")
		parser.add_argument('-c',
												'--config',
												help='Config file.',
												default="default_config.json")
		args = parser.parse_args()

		main(args)
