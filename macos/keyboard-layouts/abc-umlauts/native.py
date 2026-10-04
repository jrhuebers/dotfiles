"""Read public macOS keyboard layout APIs; never changes the selected input source."""
import ctypes as C
cf = C.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
carbon = C.CDLL('/System/Library/Frameworks/Carbon.framework/Carbon')
def bind(lib, name, restype, args):
    f = getattr(lib, name); f.restype = restype; f.argtypes = args; return f
ptr = C.c_void_p
array_count = bind(cf, 'CFArrayGetCount', C.c_long, [ptr])
array_get = bind(cf, 'CFArrayGetValueAtIndex', ptr, [ptr, C.c_long])
get_string = bind(cf, 'CFStringGetCString', C.c_bool, [ptr, ptr, C.c_long, C.c_uint32])
data_length = bind(cf, 'CFDataGetLength', C.c_long, [ptr])
data_bytes = bind(cf, 'CFDataGetBytePtr', ptr, [ptr])
source_list = bind(carbon, 'TISCreateInputSourceList', ptr, [ptr, C.c_bool])
property_get = bind(carbon, 'TISGetInputSourceProperty', ptr, [ptr, ptr])
translate = bind(carbon, 'UCKeyTranslate', C.c_int32, [ptr, C.c_uint16, C.c_uint16, C.c_uint32, C.c_uint32, C.c_uint32, C.POINTER(C.c_uint32), C.c_uint32, C.POINTER(C.c_uint32), ptr])
def property(source, name):
    return property_get(source, ptr.in_dll(carbon, name))
def text(value):
    buf = C.create_string_buffer(1024)
    assert get_string(value, buf, len(buf), 0x08000100)
    return buf.value.decode()
def sources():
    items = source_list(None, True)
    return [(text(property(array_get(items, i), 'kTISPropertyInputSourceID')), array_get(items, i)) for i in range(array_count(items))]
def layout(source):
    data = property(source, 'kTISPropertyUnicodeKeyLayoutData')
    return C.string_at(data_bytes(data), data_length(data)) if data else None
if __name__ == '__main__':
    from pathlib import Path
    source = next(s for name, s in sources() if name == 'com.apple.keylayout.ABC')
    raw = layout(source)
    Path(__file__).with_name('ABC.uchr').write_bytes(raw)
    print('Exported actual system ABC:', len(raw), 'bytes')
