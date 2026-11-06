"""Ask macOS to compile the XML and compare its behavior to native ABC."""
from pathlib import Path
import ctypes as C
from native import *
import struct

path = Path.home() / 'Library/Keyboard Layouts/ABC - Umlauts.keylayout'
make_url = bind(cf, 'CFURLCreateFromFileSystemRepresentation', ptr, [ptr, C.c_char_p, C.c_long, C.c_bool])
register = bind(carbon, 'TISRegisterInputSource', C.c_int32, [ptr])
encoded = str(path).encode()
url = make_url(None, encoded, len(encoded), False)
status = register(url)
assert status == 0, f'TISRegisterInputSource failed: {status}'
items = sources()
customs = [(name, s) for name, s in items if 'umlaut' in name.lower()]
print('Registered:', [name for name, s in customs])
assert len(customs) == 1, 'Compiled layout is not available'
abc = layout(next(s for name, s in items if name == 'com.apple.keylayout.ABC'))
assert abc, 'No built-in ABC Unicode layout data'
custom = layout(customs[0][1])
assert custom, 'No compiled Unicode layout data'

def result(raw, hardware, modifier, key, state):
    statevar = C.c_uint32(state)
    length = C.c_uint32()
    output = (C.c_uint16 * 16)()
    status = translate(raw, key, 0, modifier, hardware, 0, C.byref(statevar), 16, C.byref(length), output)
    assert status == 0, status
    text = bytes(output)[:length.value * 2].decode('utf-16-le')
    return text, statevar.value

# ABC's five dead-key states have explicit numeric identifiers in the XML.
termoff = struct.unpack_from('<I', abc, 12+20)[0]
states = range(struct.unpack_from('<H', abc, termoff+2)[0]+1)
hardware_types = [0, 18, 21, 22, 23, 30, 194, 197, 200, 201, 206, 207, 40, 41, 42]
checks = changes = 0
for hardware in hardware_types:
    for modifier in range(256):
        for key in range(128):
            modified = modifier & (8|64) and not modifier & (1|16|128) and key in (0, 31, 32)
            for state in states:
                original = result(abc, hardware, modifier, key, state)
                actual = result(custom, hardware, modifier, key, state)
                if modified:
                    character = {0:'ä', 31:'ö', 32:'ü'}[key]
                    if modifier & (2|4|32):
                        character = character.upper()
                    # A pending unrelated accent terminates before a direct umlaut.
                    prefix = result(abc, hardware, 0, 49, state)[0] if state else ''
                    expected = (prefix + character, 0)
                    assert actual == expected, ('override', hardware, modifier, key, state, actual, expected)
                    changes += original != actual
                else:
                    assert actual == original, ('unexpected change', hardware, modifier, key, state, original, actual)
                checks += 1
print(f'PASS: {checks:,} native UCKeyTranslate comparisons; {changes:,} intended changes, zero unexpected differences.')
print('All hardware variants, all 256 modifier masks, all 128 key codes, all dead-key states checked.')
