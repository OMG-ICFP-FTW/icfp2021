#!/usr/bin/env python

# %%
import ctypes
from ctypes import c_uint16, Structure

class POINT(Structure):
    _pack_ = 1
    _fields_ = [("x", c_uint16),
                ("y", c_uint16)]

class PAIR(Structure):
    _pack_ = 1
    _fields_ = [("a", POINT),
                ("b", POINT)]

# # try parsing some bytes
data = bytearray(b'\x23\x00\x42\x00\x07\x00\x0f\x00')

# ctypes.sizeof(PAIR)

pair = PAIR.from_buffer(data)

pair.a.x, pair.a.y, pair.b.x, pair.b.y