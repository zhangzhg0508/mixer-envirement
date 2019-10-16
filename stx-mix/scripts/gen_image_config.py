#! /usr/bin/env python
import json

bundle_list = "bundles_to_install.lst"
config_template = "template-image-config.json"
output = "../release-image-config.json"

def main():
    # load existing image config template
    with open(config_template, "r") as read_file:
        cfg = json.load(read_file)

    bundles = cfg["Bundles"]

    #add bundles in mixbundle to image config
    with open(bundle_list, "r") as read_file:
        for line in read_file:
            line = line.strip()
            if line.startswith("#") or len(line) <= 1:
                continue
            else:
                bundles.append(line)

    #output config file
    with open(output, "w") as write_file:
        json.dump(cfg, write_file, indent=4)

if __name__ == "__main__":
    main()
