"""Losslessly convert the installed ABC uchr tables, overriding only umlaut keys."""
from pathlib import Path
import struct
from collections import defaultdict

ROOT = Path(__file__).parent
b = (ROOT / 'ABC.uchr').read_bytes()
def unpack(fmt, offset):
    return struct.unpack_from('<' + fmt, b, offset)
def entity(s):
    return ''.join(f'&#x{ord(c):04X};' for c in s)
headers = [unpack('7I', 12 + 28*i) for i in range(unpack('I', 8)[0])]
assert unpack('H', 0)[0] == 0x1002
_, default, count = unpack('HHI', headers[0][2])
mods = list(b[headers[0][2]+8:headers[0][2]+8+count])
mods += [default] * (256-len(mods))
assert all(h[2] == headers[0][2] and h[4:] == headers[0][4:] for h in headers), 'Unsupported per-hardware modifiers or state tables'
seqoff = headers[0][6]
_, seqcount = unpack('HH', seqoff)
seqoffsets = unpack('H'*(seqcount+1), seqoff+4)
def char(v):
    if v in (0xfffe, 0xffff):
        return ''
    if v & 0xc000 == 0x8000 and (v & 0x3fff) < seqcount:
        idx = v & 0x3fff
        return b[seqoff+seqoffsets[idx]:seqoff+seqoffsets[idx+1]].decode('utf-16-le')
    return chr(v)
# Exact modifiers keep Command/Control combinations completely unchanged.
# Caps+Option is the capital-letter form, as is Shift+Option.
overrides = {}
for m in range(256):
    if m & (8|64) and not m & (1|16|128):
        upper = bool(m & (2|4|32))
        pair = (mods[m], upper)
        if pair not in overrides:
            overrides[pair] = 8 + len(overrides)
        mods[m] = overrides[pair]

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">',
         '<keyboard group="0" id="16300" name="ABC - Umlauts" maxout="4">', '<layouts>']
sets = {off: f'maps{i}' for i, off in enumerate(dict.fromkeys(h[3] for h in headers))}
for first, last, mo, table, state, term, seq in headers:
    lines.append(f'<layout first="{first}" last="{last}" modifiers="abcModifiers" mapSet="{sets[table]}"/>')
lines += ['</layouts>', f'<modifierMap id="abcModifiers" defaultIndex="{default}">']
groups = defaultdict(list)
for m, table in enumerate(mods):
    groups[table].append(m)
names = ['command', 'shift', 'caps', 'option', 'control', 'rightShift', 'rightOption', 'rightControl']
for table, masks in sorted(groups.items()):
    lines.append(f'<keyMapSelect mapIndex="{table}">')
    for mask in masks:
        keys = ' '.join(name for i, name in enumerate(names) if mask & (1 << i))
        lines.append(f'<modifier keys="{keys}"/>')
    lines.append('</keyMapSelect>')
lines.append('</modifierMap>')
for off, name in sets.items():
    _, size, n = unpack('HHI', off)
    assert n == 8
    offsets = unpack('I'*n, off+8)
    tables = [unpack('H'*size, p) for p in offsets]
    lines.append(f'<keyMapSet id="{name}">')
    for idx, table in enumerate(tables):
        lines.append(f'<keyMap index="{idx}">')
        for key, value in enumerate(table):
            if value & 0xc000 == 0x4000:
                lines.append(f'<key code="{key}" action="action{value & 0x3fff}"/>')
            else:
                text = char(value)
                if text:
                    lines.append(f'<key code="{key}" output="{entity(text)}"/>')
        lines.append('</keyMap>')
    for (base, upper), idx in overrides.items():
        lines.append(f'<keyMap index="{idx}" baseMapSet="{name}" baseIndex="{base}">')
        for key, text in [(0, 'ä'), (31, 'ö'), (32, 'ü')]:
            lines.append(f'<key code="{key}" output="{entity(text.upper() if upper else text)}"/>')
        lines.append('</keyMap>')
    lines.append('</keyMapSet>')
stateoff = headers[0][4]
_, n = unpack('HH', stateoff)
stateoffsets = unpack('I'*n, stateoff+4)
lines.append('<actions>')
def when(state, value, nextstate):
    attrs = f'state="{state}" output="{entity(char(value))}"'
    if nextstate:
        attrs += f' next="{nextstate}"'
    return f'<when {attrs}/>'
for i, off in enumerate(stateoffsets):
    zerochar, zeronext, entries, fmt = unpack('HHHH', off)
    lines += [f'<action id="action{i}">', when('none', zerochar, zeronext)]
    for j in range(entries):
        if fmt == 1:
            state, value = unpack('HH', off+8+4*j)
            lines.append(when(state, value, 0))
        elif fmt == 2:
            state, span, delta, value, nextstate = unpack('HBBHH', off+8+8*j)
            for k in range(span+1):
                lines.append(when(state+k, value+k*delta if value < 0xfffe else value, nextstate+k*delta if nextstate else 0))
        else:
            raise ValueError(fmt)
    lines.append('</action>')
lines += ['</actions>', '<terminators>']
termoff = headers[0][5]
_, n = unpack('HH', termoff)
for state, value in enumerate(unpack('H'*n, termoff+4), 1):
    lines.append(when(state, value, 0))
lines += ['</terminators>', '</keyboard>']
output = ROOT / 'ABC - Umlauts.keylayout'
output.write_text('\n'.join(lines)+'\n')
print('Created', output, 'with', len(sets), 'hardware map sets; override tables:', overrides)
