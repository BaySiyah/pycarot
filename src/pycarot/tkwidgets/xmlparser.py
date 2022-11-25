from enum import Enum, auto
import os
import xml.etree.ElementTree as etree
from dataclasses import dataclass, field
from typing import Any, Self
from xml.etree.ElementTree import Element
from tkinter import ttk
import tkinter as tk

import glob


class Node:
    def get(self) -> dict:
        pass


@dataclass
class LayoutElement:
    name: str
    side: str = None
    sticky: str = None
    expand: str = None
    border: str = None
    unit: str = None
    children: list[Self] = field(default_factory=list)

    def get(self) -> dict:
        keys = vars(self).copy()
        keys.pop("name")
        keys.pop("children")
        attrib = {k: v for k, v in keys.items() if v is not None}
        if self.children:
            attrib["children"] = [x.get() for x in self.children]
        return (self.name, attrib)


@dataclass
class Layout:
    name: str
    elements: list[LayoutElement] = field(default_factory=list)

    def get(self) -> tuple[str, Any]:
        return [x.get() for x in self.elements]


@dataclass
class Statespec:
    state: str
    value: str

    def get(self) -> tuple[str, str]:
        return (self.state, self.value)


@dataclass
class Value:
    name: str
    values: list[Statespec] = field(default_factory=list)

    def get(self) -> list[tuple[str, str]]:
        return [x.get() for x in self.values]


@dataclass
class Map:
    name: str
    options: list[Value] = field(default_factory=list)

    def get(self) -> dict:
        return {x.name: x.get() for x in self.options}


@dataclass
class ConfigureOption:
    name: str
    value: str


@dataclass
class Configure:
    name: str
    options: list[ConfigureOption] = field(default_factory=list)

    def get(self) -> dict:
        return {x.name: x.value for x in self.options}


@dataclass
class ElementCreate:
    type: str
    name: str
    arguments: list[Statespec] = field(default_factory=list)
    values: list[Value] = field(default_factory=list)


def load_configure(node: Element) -> dict:
    output = {}
    for child in node:
        if child.tag != "value":
            raise Exception("XML Format: only value nodes in configure allowed")
        key = child.attrib.get("key", None)
        if key is None:
            raise Exception("XML Format: no key attribute in value node")
        value = child.attrib.get("value", None)
        if value is None:
            raise Exception("XML Format: no value attribute in value node")
        output[key] = value
    return output


def load_layout_element(node: Element, parent: LayoutElement = None) -> LayoutElement:
    if parent is None:
        parent = LayoutElement(**node.attrib)
    for child in node:
        if child.tag != "element":
            continue
        element = LayoutElement(**child.attrib)
        style = ttk.Style()
        print(element.name, "=", style.element_options(element.name))
        parent.children.append(element)
        load_layout_element(child, element)
    return parent


def append_layout_children(node: Element) -> dict:
    output = []
    for child in node:
        if child.tag != "element":
            raise Exception("XML Format: only element nodes in element allowed")
        name = child.attrib.pop("name", None)
        if name is None:
            raise Exception("XML Format: no name attribute in element node")
        output.append((name, append_layout_children(child)))
    if output:
        node.attrib["children"] = output
    return node.attrib


def load_layout(node: Element) -> list:
    output = []
    for child in node:
        if child.tag != "element":
            raise Exception("XML Format: only element nodes in layout allowed")
        name = child.attrib.pop("name", None)
        if name is None:
            raise Exception("XML Format: no name attribute in element node")
        output.append((name, append_layout_children(child)))
    return output


def load_map(node: Element) -> dict:
    output = {}
    for child in node:
        if child.tag != "mapoption":
            raise Exception("XML Format: only mapoption nodes in map allowed")
        name = child.attrib.get("name", None)
        if name is None:
            raise Exception("XML Format: no name attribute in mapoption node")
        statespecs = []
        for c in child:
            if child.tag != "statespec":
                raise Exception("XML Format: only statespec nodes in mapoption allowed")
            state = c.attrib.get("state", None)
            if state is None:
                raise Exception("XML Format: no state attribute in statespec node")
            value = c.attrib.get("value", None)
            if value is None:
                raise Exception("XML Format: no value attribute in statespec node")
            statespecs.append(tuple(state.split() + [value]))
        output[name] = statespecs
    return output


def load_create_element(node: Element) -> tuple[str, dict]:
    pass


class Style:
    def __init__(self, node: Element) -> None:
        self.name = node.attrib.get("name", None)
        if self.name is None:
            raise Exception("XML Format: style has no name attribute")
        self.table = {}
        for child in node:
            if child.tag == "configure":
                self.table[child.tag] = load_configure(child)
            elif child.tag == "layout":
                self.table[child.tag] = load_layout(child)
            elif child.tag == "map":
                self.table[child.tag] = load_map(child)
            elif child.tag == "layout":
                name, value = load_create_element(child)
                self.table[name] = value


class XmlStyle:
    def __init__(self, xml: str) -> None:
        tree = etree.parse(xml)
        root = tree.getroot()

        self.styles: list[Style] = []
        for child in root:
            if child.tag != "style":
                raise Exception("XML Format: only style nodes in root node allowed")
            self.styles.append(Style(child))
        [print(x) for x in self.styles]

    def settings(self) -> dict:
        return {x.name: x.table for x in self.styles}


def load_layout_element(node: Element, parent: LayoutElement = None) -> LayoutElement:
    if parent is None:
        parent = LayoutElement(**node.attrib)
    for child in node:
        if child.tag != "element":
            continue
        element = LayoutElement(**child.attrib)
        style = ttk.Style()
        print(element.name, "=", style.element_options(element.name))
        parent.children.append(element)
        load_layout_element(child, element)
    return parent


def create_layout(node: Element) -> Layout:
    layout = Layout(**node.attrib)
    for child in node:
        layout.elements.append(load_layout_element(child))
    return layout


def create_configure(node: Element) -> Configure:
    config = Configure(**node.attrib)
    for child in node:
        if child.tag != "option":
            continue
        config.options.append(ConfigureOption(**child.attrib))
    return config


def create_map(node: Element) -> Map:
    map = Map(**node.attrib)
    for child in node:
        if child.tag != "mapoption":
            continue
        option = Value(**child.attrib)
        for e in child:
            if e.tag != "mapvalue":
                continue
            option.values.append(Statespec(**e.attrib))
        map.options.append(option)
    return map


images = {}


def _load_images(path: str) -> None:
    path = os.path.abspath(path)
    for f in glob.glob(f"{path}/*.gif"):
        img = os.path.basename(f)
        name = img.removesuffix(".gif")
        images[name] = tk.PhotoImage(name, file=f, format="gif89")


def initialize(path: str) -> None:
    _load_images(path)

    xml = XmlStyle("./src/pycarot/tkwidgets/style.xml")

    style = ttk.Style()
    settings = xml.settings()
    style.theme_create("pycarot", "default", settings=settings)
    style.theme_use("pycarot")

    # for x in xml.layouts:
    #     style.layout(x.name, x.get())

    # for x in xml.configs:
    #     style.configure(x.name, **x.get())

    # for x in xml.maps:
    #     style.map(x.name, **x.get())
