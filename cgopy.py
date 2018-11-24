__all__ = [ 'libgobgp', '_PATTRS_CAP', '_AF_NAME', 'Buf', 'Path', 'unpack_buf', 'protobuf_obj_attrs', ]

from ctypes import c_int, c_char, c_char_p, POINTER, Structure, cdll
from struct import unpack

# import os
# libgobgp = cdll.LoadLibrary(os.environ["GOPATH"] + "/src/github.com/osrg/gobgp/gobgp/lib/libgobgp.so")

libgobgp = cdll.LoadLibrary("/opt/go/src/github.com/osrg/gobgp/gobgp/lib/libgobgp.so")

_PATTRS_CAP = 32
_AF_NAME = dict([(4, "ipv4-unicast"), (6, "ipv6-unicast"), ])


class Buf(Structure):
  _fields_ = [("value", POINTER(c_char)),
              ("len", c_int),
             ]


class Path(Structure):
  _fields_ = [("nlri", Buf),
              ("path_attributes", POINTER(POINTER(Buf) * _PATTRS_CAP)),
              ("path_attributes_len", c_int),
              ("path_attributes_cap", c_int),
             ]


libgobgp.serialize_path.restype = POINTER(Path)
libgobgp.serialize_path.argtypes = (c_int, c_char_p)
libgobgp.decode_path.restype = c_char_p
libgobgp.decode_path.argtypes = (POINTER(Path),)


def unpack_buf(buf):
  return unpack(str(buf.len) + "s", buf.value[:buf.len])[0]


def protobuf_obj_attrs(o):
  slice_ind = -1 * len('_FIELD_NUMBER')
  return [ attr[:slice_ind].lower() for attr in dir(o) if attr.endswith('_FIELD_NUMBER') ]


if __name__ == '__main__':
  pass
