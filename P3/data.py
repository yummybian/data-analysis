#!/usr/bin/env python
# encoding: utf-8

import xml.etree.cElementTree as ET
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]
ADDRESS = ["addr:housenumber", "addr:postcode", "addr:street", "addr:city"]
KFC = [u"kfc", u"肯德基"]
MC = [u"mcdonald", u"麦当劳"]


def is_kfc(name):
    for x in KFC:
        if x in name.lower():
            return True

    return False


def is_mc(name):
    for x in MC:
        if x in name.lower():
            return True

    return False


def correct_city(name):
    if u"wuhan" in name or u"武汉" in name:
        return u"武汉"
    elif u"汉川" in name:
        return u"汉川"
    else:
        return name


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":
        created_dict = {}
        addr_dict = {}
        node_refs = []
        node["type"] = element.tag
        if "id" in element.attrib:
            node["id"] = element.attrib["id"]
        if "visible" in element.attrib:
            node["visible"] = element.attrib["visible"]
        if "lat" in element.attrib and "lon" in element.attrib:
            lat = float(element.attrib["lat"])
            lon = float(element.attrib["lon"])
            node["pos"] = [lat, lon]
        for key in CREATED:
            created_dict[key] = element.attrib.get(key, "")
        if created_dict:
            node["created"] = created_dict
        # 迭代二级tag标签
        for tag in element.iter("tag"):
            if tag.attrib["k"] in ADDRESS:
                addr_dict[tag.attrib["k"].split(":")[1]] = tag.attrib["v"]
            elif tag.attrib["k"] in ("name", "name:en", "name:zh"):
                # 统一为中文名
                if is_kfc(tag.attrib["v"]):
                    cnt["kfc"] = cnt["kfc"] + 1
                    node["name"] = "肯德基"
                elif is_mc(tag.attrib["v"]):
                    cnt["mc"] = cnt["mc"] + 1
                    node["name"] = "麦当劳"
                else:
                    node["name"] = tag.attrib["v"]
            elif tag.attrib["k"] == "amenity":
                node["amenity"] = tag.attrib["v"]
            elif tag.attrib["k"] == "phone":
                node["phone"] = tag.attrib["v"]

        if addr_dict:
            # 整理城市名称
            if "city" in addr_dict: 
                addr_dict["city"] = correct_city(addr_dict["city"])
            node["address"] = addr_dict

        # 迭代二级nd标签
        for nd in element.iter("nd"):
            node_refs.append(nd.attrib["ref"])
        if node_refs:
            node["node_refs"] = node_refs
        return node
    else:
        return None


def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def test():
    '''
    NOTE: if you are running this code on your computer, with a larger dataset,
    call the process_map procedure with pretty=False. The pretty=True option adds
    additional spaces to the output, making it significantly larger.
    '''
    process_map("wuhan_china.osm", True)


if __name__ == "__main__":
    test()
