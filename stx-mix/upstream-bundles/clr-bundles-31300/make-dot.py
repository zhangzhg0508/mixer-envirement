#!/usr/bin/env python3
import re
import glob
import os
import collections

statuscolordict = {'Active':'green', 'WIP':'darkorange1', 'Deprecated':'red'}

def main():
        bundledict = build_bundle_dictionary()
        statusbundledict = build_statusbundle_dictionary(bundledict)
        subgraphs = generate_subgraphs(statusbundledict)
        edges = generate_edges(bundledict)
        print_dot_output(subgraphs, edges)

def build_bundle_dictionary():
        bundledict = {}
        namepattern = re.compile('(?<=\[TITLE\]: ).+')
        statuspattern = re.compile('(?<=\[STATUS\]: ).+')
        includepattern = re.compile('(?<=include\().+(?=\))')
        packagepattern = re.compile('^[^\(\)#\\n]+$', re.MULTILINE)
        for filename in glob.glob(os.path.dirname(os.path.realpath(__file__)) + '/bundles/*'):
                with open(filename, 'r') as bundlefile:
                        bundledef = bundlefile.read()
                        if namepattern.search(bundledef) != None and statuspattern.search(bundledef) != None:
                            bundlename = namepattern.findall(bundledef)[0]
                            bundlestatus = statuspattern.findall(bundledef)[0]
                            bundleincludes = includepattern.findall(bundledef)
                            bundlepackages = packagepattern.findall(bundledef)
                            bundledict[bundlename] = Bundle(bundlename, bundlestatus, bundleincludes, bundlepackages)
        with open('packages', 'r') as package_file:
                re_strip_comment = re.compile("#.*$")
                for line in package_file:
                        line = re_strip_comment.sub("", line)
                        line = line.strip()
                        if not line:
                            continue
                        bundledict[line] = Bundle(line, 'Active', [], line)
        return bundledict

def build_statusbundle_dictionary(bundledict):
        statusbundledict = collections.defaultdict(list)
        for bundlename in bundledict.keys():
                statusbundledict[bundledict[bundlename].status].append(bundlename)
        return statusbundledict

def generate_subgraphs(statusbundledict):
        subgraphs = []
        for status in statusbundledict.keys():
                if status in statuscolordict:
                    subgraphnodes = ['node [color = ' + statuscolordict[status] + ']', 'label = <<b>' + status.upper() + '</b>>']
                    for bundle in statusbundledict[status]:
                            subgraphnodes.append('"' + bundle + '";')
                    subgraphs.append('subgraph cluster_' + status.lower() + ' {\n\t\t' + '\n\t\t'.join(subgraphnodes) + '\n\t}')
        return subgraphs

def generate_edges(bundledict):
        edges = []
        for bundlename, bundle in bundledict.items():
                for includename in bundle.includes:
                        includebundle = bundledict[includename]
                        edges.append('"' + bundlename + '" -> "' + includename + '" [color = ' + determine_edge_color(bundle, includebundle) + ', tooltip = "' + bundlename + ' -> ' + includename + '"];')
        return edges

def determine_edge_color(bundle, includebundle):
    if bundle.status in statuscolordict and includebundle.status in statuscolordict:
        bundlecolor = statuscolordict[bundle.status]
        includebundlecolor = statuscolordict[includebundle.status]
        if bundlecolor == includebundlecolor:
                return bundlecolor
        else:
                return includebundlecolor
    else:
        return 'black'

def print_dot_output(subgraphs, edges):
        fontname = 'sans-serif'
        print('digraph {')
        print('\tgraph [layout = dot, fontname = "' + fontname + '", penwidth = 4]')
        print('\tnode [fontname = "' + fontname + '", style = filled, fontcolor = white]')
        print('\tedge [fontname = "' + fontname + '", penwidth = 2]')
        print('\t' + '\n\t'.join(subgraphs))
        print('\t' + '\n\t'.join(edges))
        print('}')

class Bundle:
        def __init__(self, name, status, includes, packages):
                self.name = name
                self.status = status
                self.includes = includes
                self.packages = packages

if __name__ == "__main__":
    main()

