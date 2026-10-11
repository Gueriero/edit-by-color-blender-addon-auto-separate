# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# OrcaSlicer G-code -> Blender curves.
#
# Why a separate module: __init__.py is the KIRI addon core (UI + mesh pipeline).
# This is a file-format reader with its own state machine and its own self-test,
# and it is the only part of the addon that must be importable headlessly.
#
# Pipeline: probe header/config for tools + palette -> stream-parse the body into
# polyline paths bucketed by (tool, feature) -> one curve object per bucket with a
# round bevel (bevel_depth = line width / 2) so the print can be rendered.

import array
import math
import os
import re
import time
from collections import Counter

import bpy
from bpy_extras.io_utils import ImportHelper

try:  # normal case: loaded as part of the addon package
    from . import _SNA_DIALOG_STASH, _sna_stash_update
except Exception:  # standalone import (headless test harness)
    _SNA_DIALOG_STASH = {}

    def _sna_stash_update(key, store):
        _SNA_DIALOG_STASH[key] = store


COLL_NAME = 'GCODE Import'
MM = 0.001  # scene is metric, 1 BU = 1 m

# Buckets the UI can gate. Keys are stable, labels only feed the panel.
FEATURES = (
    ('walls', 'Walls (perimeters)'),
    ('surfaces', 'Top / bottom surfaces'),
    ('infill', 'Infill'),
    ('supports', 'Supports'),
    ('skirt', 'Skirt / Brim'),
    ('travel', 'Travel moves'),
)

_DEFAULT_COLORS = (
    '#FF8000', '#008000', '#0000FF', '#FF0000', '#FFFF00',
    '#8000FF', '#00FFFF', '#FF00FF', '#FFFFFF', '#808080',
)

_SNA_GCODE_STASH_KEY = 'sna_gcode_last_settings'
_SNA_GCODE_PERSIST = (
    'keep_walls', 'keep_surfaces', 'keep_infill', 'keep_supports', 'keep_skirt',
    'keep_travel', 'skip_start', 'simplify', 'simplify_angle', 'width_mm',
    'bevel_resolution', 'per_feature', 'replace_existing',
)


def _icon(value):
    try:
        items = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items
        if value in items.keys():
            return items[value].value
    except Exception:
        pass
    return 0


def _compact(n):
    if n >= 1_000_000:
        return f'{n / 1e6:.1f}M'.replace('.0M', 'M')
    if n >= 1_000:
        return f'{n / 1e3:.0f}k'
    return str(int(n))


# --------------------------------------------------------------------------- colors

def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_rgba(text, fallback=(0.8, 0.8, 0.8)):
    """'#RRGGBB' -> linear RGBA tuple. Blender base color sockets are linear."""
    s = (text or '').strip().lstrip('#')
    if len(s) < 6:
        return (fallback[0], fallback[1], fallback[2], 1.0)
    try:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
    except ValueError:
        return (fallback[0], fallback[1], fallback[2], 1.0)
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b), 1.0)


def parse_hex_list(text):
    """Orca writes '#FF8000;#008000'. Older builds concatenate without ';'."""
    out = []
    for chunk in (text or '').split(';'):
        chunk = chunk.strip().strip('"')
        if chunk.startswith('#'):
            chunk = chunk[1:]
        digits = ''.join(c for c in chunk if c in '0123456789abcdefABCDEF')
        for i in range(0, len(digits) - 5, 6):
            out.append(digits[i:i + 6].upper())
    return out


# --------------------------------------------------------------------------- features

def categorize(type_text):
    """Map an Orca extrusion-role string onto a UI bucket.

    Order matters ('Internal solid infill' must not land in surfaces) and the match
    is substring-based on purpose: Orca localises these strings, so an exact table
    would silently break on a non-English UI.
    """
    t = (type_text or '').lower()
    if not t:
        return 'walls'
    if 'support' in t:
        return 'supports'
    if 'skirt' in t or 'brim' in t:
        return 'skirt'
    if 'travel' in t or 'move' in t:
        return 'travel'
    if 'infill' in t or 'fill' in t or 'ironing' in t:
        return 'infill'
    if 'surface' in t or 'skin' in t or 'bridge' in t:
        return 'surfaces'
    if 'wall' in t or 'perimeter' in t or 'shell' in t:
        return 'walls'
    return 'walls'  # prime tower, custom, unknown — real geometry, better kept


# --------------------------------------------------------------------------- probe

def probe_gcode(path):
    """Head+tail scan only. Populates the panel before the full parse runs.

    Returns: tools (sorted list), colors (hex list from the config block),
    has_features (;TYPE: comments present), line_width (float or None),
    filament_types, uses_ams, size_bytes.
    """
    head = 512 * 1024
    size = os.path.getsize(path)
    chunks = []
    with open(path, 'rb') as fh:
        chunks.append(fh.read(head))
        if size > head:
            fh.seek(max(0, size - head))
            chunks.append(fh.read(head))
    data = b''.join(chunks).decode('utf-8', 'replace')

    tools = set()
    colors = []
    ftypes = []
    widths = []
    has_features = False
    uses_ams = False

    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if line[0] == ';':
            body = line[1:].strip()
            low = body.lower()
            if low.startswith('type:') or low.startswith('type :'):
                has_features = True
            elif '=' in body:
                key, _, value = body.partition('=')
                key = key.strip().lower()
                if key in ('filament_colour', 'extruder_colour'):
                    if not colors:
                        colors = parse_hex_list(value)
                elif key == 'filament_type':
                    ftypes = [v.strip() for v in value.split(';') if v.strip()]
                elif key == 'line_width':
                    for v in value.split(';'):
                        try:
                            widths.append(float(v))
                        except ValueError:
                            pass
            continue
        c0 = line[0]
        if c0 in 'Tt' and line[1:].strip().isdigit():
            tools.add(int(line[1:].strip()))
        elif line.startswith('M620'):
            uses_ams = True
        elif line.startswith('M104') or line.startswith('M109'):
            tail = line.rsplit('T', 1)
            if len(tail) == 2 and tail[1].strip().isdigit():
                tools.add(int(tail[1].strip()))

    if not tools:
        tools = {0}
    return {
        'tools': sorted(tools),
        'colors': colors,
        'filament_types': ftypes,
        'has_features': has_features,
        'line_width': widths[0] if widths else None,
        'uses_ams': uses_ams,
        'size_bytes': size,
    }


def probe_summary(info):
    bits = [f'{len(info["tools"])} tool(s)']
    if info['colors']:
        bits.append(f'palette: {len(info["colors"])} colors from config')
    else:
        bits.append('no palette in file')
    bits.append(';TYPE: yes' if info['has_features'] else ';TYPE: none')
    if info['uses_ams']:
        bits.append('AMS')
    bits.append(f'{info["size_bytes"] / 1e6:.1f} MB')
    return ' · '.join(bits)


# --------------------------------------------------------------------------- parser

_PCHARS = 'XYZEFIJR'
# No exponent group: in gcode 'E' is always the extruder parameter, so matching
# '[eE]\d+' as scientific notation turns "Y0E1" into 0e1 and swallows the E value.
_PARAM_RE = re.compile(r'([A-Za-z])\s*(-?\d*\.?\d+)')


def _command(line):
    """'G1 X0' -> 'G1', 'G01X0' -> 'G1', 'M104 S' -> 'M104'.

    Slicers normally put a space after the command, compact output does not — and
    slicing on the first three characters silently drops every compact move.
    """
    i = 1
    n = len(line)
    while i < n and line[i].isdigit():
        i += 1
    if i == 1:
        return line[:1].upper()
    return f'{line[0].upper()}{int(line[1:i])}'


def _params(line):
    """Parse G-code parameters. Fast path: whitespace-separated (what slicers emit).

    Anything else — a line with no whitespace at all (G1X10Y0E1), or a token that
    packs several parameters — goes through the regex.
    """
    out = {}
    if ' ' in line or '\t' in line:
        ok = True
        for tok in line.split():
            if len(tok) < 2:
                continue
            head = tok[0].upper()
            if head not in _PCHARS:
                continue
            tail = tok[1:]
            if any(ch.isalpha() for ch in tail):
                ok = False  # compact form like X10.5Y20
                break
            try:
                out[head] = float(tail)
            except ValueError:
                ok = False
                break
        if ok:
            return out
    out = {}
    for m in _PARAM_RE.finditer(line):
        head = m.group(1).upper()
        if head in _PCHARS:
            out[head] = float(m.group(2))
    return out


def parse_gcode(path, log=None, want_travel=False, skip_start=True):
    """Stream-parse the file into polyline paths bucketed by (tool, bucket).

    Generator: yields (status_text, percent); returns the parsed dict. The modal
    operator drives it for the progress bar, tests drain it for the result.
    """
    def _log(msg):
        if log:
            log(msg)

    size = max(1, os.path.getsize(path))
    read = 0
    last_pct = 0

    paths = {}
    pos = [0.0, 0.0, 0.0]
    e_val = 0.0
    e_rel = False          # M83: E is a per-move delta
    xyz_rel = False        # G91
    tool = 0
    bucket = 'walls'
    widths = Counter()
    types_seen = Counter()
    colors = []
    line_width_cfg = None
    tools_seen = set()
    has_features = False
    in_custom = False      # inside an Orca ";TYPE:Custom" block = start/end gcode
    n_lines = n_moves = n_extrude = n_travel = 0
    n_arcs = 0

    cur = None
    cur_key = None
    last_pt = None

    def close_path():
        nonlocal cur, cur_key, last_pt
        cur = None
        cur_key = None
        last_pt = None

    def add_point(x, y, z):
        nonlocal last_pt
        if last_pt is not None:
            if abs(x - last_pt[0]) < 1e-5 and abs(y - last_pt[1]) < 1e-5 and abs(z - last_pt[2]) < 1e-5:
                return
        cur.extend((x, y, z))
        last_pt = (x, y, z)

    def begin_path(key, from_pt):
        nonlocal cur, cur_key
        close_path()
        cur = array.array('f')
        cur_key = key
        paths.setdefault(key, []).append(cur)
        add_point(from_pt[0], from_pt[1], from_pt[2])

    def move_to(nx, ny, nz, extruding):
        """One linear move; splits nothing (arcs call this per sub-segment)."""
        nonlocal n_extrude, n_travel
        if extruding:
            n_extrude += 1
            # Extrusion before the first ;TYPE: belongs to the start gcode (purge line).
            # It gets its own bucket so run_import can drop or keep it as a whole.
            key_bucket = bucket if (has_features and not in_custom) else 'pre_type'
            if cur is None or cur_key != (tool, key_bucket):
                begin_path((tool, key_bucket), pos)
            add_point(nx, ny, nz)
        else:
            n_travel += 1
            if want_travel:
                if cur is None or cur_key != (tool, 'travel'):
                    begin_path((tool, 'travel'), pos)
                add_point(nx, ny, nz)
            else:
                close_path()

    fh = open(path, 'r', encoding='utf-8', errors='replace', newline='')
    try:
        for raw in fh:
            n_lines += 1
            read += len(raw)
            if n_lines % 20000 == 0:
                pct = int(read * 60 / size)
                if pct != last_pct:
                    last_pct = pct
                    yield (f'Parsing gcode... {_compact(n_lines)} lines', pct)

            line = raw.strip()
            if not line:
                continue
            c0 = line[0]

            if c0 == ';':
                body = line[1:].strip()
                low = body.lower()
                if low.startswith('type:'):
                    value = body[5:].strip()
                    types_seen[value] += 1
                    # Orca wraps the whole start and end gcode in a "Custom" block, so it
                    # marks the purge line but says nothing about the model. Treat it as a
                    # boundary instead of a feature, or it defeats the start-gcode skip.
                    if value.lower().startswith('custom'):
                        in_custom = True
                    else:
                        in_custom = False
                        has_features = True
                    new_bucket = categorize(value)
                    if new_bucket != bucket:
                        bucket = new_bucket
                        close_path()
                elif low.startswith('width:'):
                    try:
                        widths[round(float(body[6:].strip()), 3)] += 1
                    except ValueError:
                        pass
                elif '=' in body:
                    key, _, value = body.partition('=')
                    key = key.strip().lower()
                    if key in ('filament_colour', 'extruder_colour'):
                        if not colors:
                            colors = parse_hex_list(value)
                    elif key == 'line_width':
                        try:
                            line_width_cfg = float(value.split(';')[0])
                        except ValueError:
                            pass
                continue

            if c0 in 'Mm':
                cmd = _command(line)
                if cmd == 'M82':
                    e_rel = False
                elif cmd == 'M83':
                    e_rel = True
                continue

            if c0 in 'Gg':
                cmd = _command(line)
                if cmd == 'G90':
                    xyz_rel = False
                    continue
                if cmd == 'G91':
                    xyz_rel = True
                    continue
                if cmd == 'G92':
                    par = _params(line)
                    if 'E' in par:
                        e_val = par['E']
                    if 'X' in par or 'Y' in par or 'Z' in par:
                        if 'X' in par:
                            pos[0] = par['X']
                        if 'Y' in par:
                            pos[1] = par['Y']
                        if 'Z' in par:
                            pos[2] = par['Z']
                    continue
                if cmd not in ('G0', 'G1', 'G2', 'G3'):
                    continue

                par = _params(line)

                if 'X' not in par and 'Y' not in par and 'Z' not in par:
                    # Pure extruder move (retract / prime): the nozzle does not move,
                    # so the path must survive it instead of being cut in two.
                    if 'E' in par:
                        if e_rel:
                            e_val += par['E']
                        else:
                            e_val = par['E']
                    continue

                n_moves += 1
                px, py, pz = pos

                if xyz_rel:
                    nx = px + par.get('X', 0.0)
                    ny = py + par.get('Y', 0.0)
                    nz = pz + par.get('Z', 0.0)
                else:
                    nx = par.get('X', px)
                    ny = par.get('Y', py)
                    nz = par.get('Z', pz)

                de = 0.0
                if cmd in ('G1', 'G2', 'G3') and 'E' in par:
                    if e_rel:
                        de = par['E']
                        e_val += par['E']
                    else:
                        de = par['E'] - e_val
                        e_val = par['E']
                extruding = de > 1e-6

                if cmd in ('G2', 'G3') and 'X' not in par and 'Y' not in par:
                    continue  # firmware macro, e.g. Snapmaker's "G3 Z.88 I-.042 J1.216 P1"

                if cmd in ('G2', 'G3') and ('I' in par or 'J' in par):
                    n_arcs += 1
                    cx = px + par.get('I', 0.0)
                    cy = py + par.get('J', 0.0)
                    r = math.hypot(px - cx, py - cy)
                    a0 = math.atan2(py - cy, px - cx)
                    a1 = math.atan2(ny - cy, nx - cx)
                    sweep = a1 - a0
                    if cmd == 'G2' and sweep > 0:
                        sweep -= 2 * math.pi
                    elif cmd == 'G3' and sweep < 0:
                        sweep += 2 * math.pi
                    steps = max(2, int(abs(sweep) / math.radians(8.0)) + 1)
                    for i in range(1, steps + 1):
                        f = i / steps
                        a = a0 + sweep * f
                        mx = cx + r * math.cos(a)
                        my = cy + r * math.sin(a)
                        mz = pz + (nz - pz) * f
                        move_to(mx, my, mz, extruding)
                        pos[0], pos[1], pos[2] = mx, my, mz
                    continue

                move_to(nx, ny, nz, extruding)
                pos[0], pos[1], pos[2] = nx, ny, nz
                continue

            if c0 in 'Tt':
                body = line[1:].strip()
                if body.isdigit():
                    new_tool = int(body)
                    if new_tool != tool:
                        tool = new_tool
                        tools_seen.add(tool)
                        close_path()
                continue
    finally:
        fh.close()

    close_path()

    # Start-gcode extrusion (purge / prime line) is real filament but not the model.
    # Dropped by default; kept — folded into walls — when there is no ;TYPE: info to
    # tell start gcode apart, or when the user asks for it.
    pre_type = [k for k in paths if k[1] == 'pre_type']
    if pre_type:
        keep_pre = (not has_features) or (not skip_start)
        for key in pre_type:
            plist = paths.pop(key)
            if keep_pre:
                paths.setdefault((key[0], 'walls'), []).extend(plist)

    auto_width = 0.0
    if widths:
        auto_width = widths.most_common(1)[0][0]
    else:
        auto_width = line_width_cfg or 0.0

    n_paths = sum(len(v) for v in paths.values())
    n_points = sum(len(p) // 3 for v in paths.values() for p in v)
    _log(f'Parsed {_compact(n_lines)} lines: {_compact(n_moves)} moves, '
         f'{_compact(n_extrude)} extruding, {_compact(n_travel)} travel, '
         f'{n_arcs} arcs, {_compact(n_paths)} paths, {_compact(n_points)} points')

    return {
        'paths': paths,
        'tools': sorted(tools_seen | {0}),
        'colors': colors,
        'types_seen': types_seen,
        'has_features': has_features,
        'auto_width': auto_width,
        'n_lines': n_lines,
        'n_moves': n_moves,
        'n_arcs': n_arcs,
        'n_paths': n_paths,
        'n_points': n_points,
    }


# --------------------------------------------------------------------------- simplify

def simplify_paths(parsed, angle_deg, log=None):
    """Drop points that lie on a straight line (angle < threshold).

    G-code is full of collinear vertices (arc fitting output, per-layer retrace
    splits). Removing them cuts curve geometry several-fold at no visible cost.
    """
    import numpy as np

    cos_limit = math.cos(math.radians(max(0.0, angle_deg)))
    paths = parsed['paths']
    removed = 0
    kept = 0
    total = max(1, parsed['n_points'])
    done = 0
    last_yield = 0

    for key, plist in paths.items():
        for i, arr in enumerate(plist):
            n = len(arr) // 3
            done += n
            if n < 3:
                kept += n
                continue
            pts = np.frombuffer(arr, dtype=np.float32).reshape(-1, 3).astype(np.float64)
            v1 = pts[1:-1] - pts[:-2]
            v2 = pts[2:] - pts[1:-1]
            n1 = np.linalg.norm(v1, axis=1)
            n2 = np.linalg.norm(v2, axis=1)
            denom = n1 * n2
            cos = np.einsum('ij,ij->i', v1, v2) / np.where(denom > 1e-12, denom, 1.0)
            # keep a point when the path actually turns (reversals included: |cos| would
            # hide them, so compare against the positive limit only)
            keep_mask = np.concatenate(([True], cos < cos_limit, [True]))
            out = pts[keep_mask].astype(np.float32)
            removed += n - len(out)
            kept += len(out)
            if len(out) != n:
                plist[i] = array.array('f', out.tobytes())
        # Throttle by work done, not per path: the modal operator pulls exactly one
        # yield per timer tick, so yielding too often makes the whole pass tick-bound.
        if done - last_yield >= 200000:
            last_yield = done
            yield (f'Simplifying... {_compact(done)} points', 60 + int(done * 15 / total))

    parsed['n_points'] = kept
    if log:
        log(f'Simplify: dropped {_compact(removed)} collinear points, {_compact(kept)} left')
    yield (f'Simplified: {_compact(kept)} points', 75)


# --------------------------------------------------------------------------- build

def build_curves(parsed, opts, log=None):
    """One curve object per (tool, feature). bevel_depth makes the round profile."""
    import numpy as np

    def _log(msg):
        if log:
            log(msg)

    width_mm = opts.get('width_mm') or 0.0
    if width_mm <= 0.0:
        width_mm = parsed['auto_width'] or 0.42
    bevel_depth = max(1e-6, width_mm * MM * 0.5)
    bevel_res = int(opts.get('bevel_resolution', 2))
    per_feature = bool(opts.get('per_feature', True))
    colors = opts.get('colors') or []

    coll = bpy.data.collections.get(COLL_NAME)
    if coll is not None and opts.get('replace_existing', True):
        for ob in list(coll.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.curves.remove(data)
        coll = None
    if coll is None:
        coll = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(coll)

    mats = {}

    def material_for(tool):
        if tool in mats:
            return mats[tool]
        name = f'EBC_GCODE_T{tool}'
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        rgba = colors[tool] if tool < len(colors) else hex_to_rgba(
            _DEFAULT_COLORS[tool % len(_DEFAULT_COLORS)])
        node = mat.node_tree.nodes.get('Principled BSDF') if mat.node_tree else None
        if node is not None:
            node.inputs['Base Color'].default_value = rgba
            if 'Roughness' in node.inputs:
                node.inputs['Roughness'].default_value = 0.6
        mat.diffuse_color = rgba  # solid-mode viewport
        mats[tool] = mat
        return mat

    keys = sorted(parsed['paths'].keys())
    total_splines = max(1, parsed['n_paths'])
    made = 0
    last_yield = 0
    objects = []

    for tool, bucket in keys:
        plist = parsed['paths'][(tool, bucket)]
        if not plist:
            continue
        name = f'GCODE_T{tool}' + (f'_{bucket}' if per_feature else '')
        cu = bpy.data.curves.new(name, 'CURVE')
        cu.dimensions = '3D'
        cu.resolution_u = 1          # POLY splines need no extra tessellation
        cu.bevel_depth = bevel_depth
        cu.bevel_resolution = bevel_res
        cu.use_fill_caps = True
        cu.fill_mode = 'FULL'
        ob = bpy.data.objects.new(name, cu)
        coll.objects.link(ob)
        cu.materials.append(material_for(tool))
        objects.append(ob)

        for arr in plist:
            n = len(arr) // 3
            if n < 2:
                continue
            pts = np.frombuffer(arr, dtype=np.float32).reshape(-1, 3) * MM
            co = np.ones((n, 4), dtype=np.float32)  # homogeneous w = 1
            co[:, :3] = pts
            sp = cu.splines.new('POLY')
            sp.points.add(n - 1)
            sp.points.foreach_set('co', co.ravel())
            made += 1
            if made - last_yield >= 2000:
                last_yield = made
                yield (f'Building curves... {_compact(made)} splines',
                       75 + int(made * 25 / total_splines))

    _log(f'Built {len(objects)} curve objects, {_compact(made)} splines, '
         f'bevel depth {bevel_depth * 1000:.3f} mm')

    if objects:
        try:
            bpy.context.view_layer.objects.active = objects[0]
        except Exception:
            pass

    yield ('Done', 100)
    return {
        'objects': len(objects),
        'splines': made,
        'bevel_depth': bevel_depth,
        'collection': coll.name,
    }


def _drain(gen):
    """Run a status generator to completion and return its value (test helper)."""
    while True:
        try:
            next(gen)
        except StopIteration as stop:
            return stop.value


def run_import(path, opts, log=None):
    """Generator driving the whole pipeline; yields (text, pct); returns summary."""
    yield ('Reading gcode...', 0)
    parsed = yield from parse_gcode(
        path, log,
        want_travel=bool(opts.get('keep_travel', False)),
        skip_start=bool(opts.get('skip_start', True)),
    )
    if opts.get('simplify', True):
        yield from simplify_paths(parsed, opts.get('simplify_angle', 0.5), log)
    keep = {f for f, _ in FEATURES if opts.get(f'keep_{f}', True)}
    if parsed['has_features']:
        for key in list(parsed['paths'].keys()):
            if key[1] not in keep:
                del parsed['paths'][key]
    summary = yield from build_curves(parsed, opts, log)
    summary['tools'] = parsed['tools']
    summary['parsed'] = parsed
    return summary


# --------------------------------------------------------------------------- UI

class SNA_GcodeColor(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(
        name='Color', subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )


class SNA_OT_gcode_browse(bpy.types.Operator, ImportHelper):
    bl_idname = 'sna.gcode_browse'
    bl_label = 'Pick G-code File'
    bl_description = 'Choose a sliced .gcode file (OrcaSlicer / Bambu / Prusa dialects)'

    filename_ext = '.gcode'
    filter_glob: bpy.props.StringProperty(default='*.gcode;*.gco;*.g;*.txt', options={'HIDDEN'})

    def execute(self, context):
        sc = context.scene
        sc.sna_gcode_path = self.filepath
        try:
            info = probe_gcode(self.filepath)
        except Exception as e:
            sc.sna_gcode_info = f'Unreadable: {e}'
            self.report({'ERROR'}, f'Cannot read gcode: {e}')
            return {'CANCELLED'}
        sc.sna_gcode_info = probe_summary(info)
        sc.sna_gcode_has_features = info['has_features']
        _fill_scene_colors(sc, info['tools'], info['colors'])
        self.report({'INFO'}, f'G-code: {probe_summary(info)}')
        return {'FINISHED'}


def _fill_scene_colors(sc, tools, hex_colors):
    """Sync the scene's tool-color list with the file.

    Colors the file does not carry stay as the user set them; fresh slots start from
    the built-in cycle so a palette-less file still gives visually distinct tools.
    """
    want = max(1, len(tools))
    while len(sc.sna_gcode_colors) > want:
        sc.sna_gcode_colors.remove(len(sc.sna_gcode_colors) - 1)
    while len(sc.sna_gcode_colors) < want:
        sc.sna_gcode_colors.add()
        i = len(sc.sna_gcode_colors) - 1
        src = hex_colors[i] if i < len(hex_colors) else _DEFAULT_COLORS[i % len(_DEFAULT_COLORS)]
        sc.sna_gcode_colors[i].color = hex_to_rgba(src)
    for i in range(min(want, len(hex_colors))):
        sc.sna_gcode_colors[i].color = hex_to_rgba(hex_colors[i])


def _stash_gcode_settings(op, context=None):
    if not getattr(op, '_dialog_open', False):
        return
    store = {}
    for name in _SNA_GCODE_PERSIST:
        try:
            store[name] = getattr(op, name)
        except Exception:
            pass
    try:
        store['colors'] = [list(i.color) for i in bpy.context.scene.sna_gcode_colors]
        store['path'] = bpy.context.scene.sna_gcode_path
    except Exception:
        pass
    _sna_stash_update(_SNA_GCODE_STASH_KEY, store)


def _restore_gcode_settings(op, context):
    sc = context.scene
    store = _SNA_DIALOG_STASH.get(_SNA_GCODE_STASH_KEY) or {}
    for name in _SNA_GCODE_PERSIST:
        if name in store:
            try:
                setattr(op, name, store[name])
            except Exception:
                pass
    if not sc.sna_gcode_path and store.get('path'):
        sc.sna_gcode_path = store['path']
    colors = store.get('colors')
    if colors:
        while len(sc.sna_gcode_colors) > len(colors):
            sc.sna_gcode_colors.remove(len(sc.sna_gcode_colors) - 1)
        while len(sc.sna_gcode_colors) < len(colors):
            sc.sna_gcode_colors.add()
        for i, rgba in enumerate(colors):
            sc.sna_gcode_colors[i].color = rgba


class SNA_OT_gcode_import(bpy.types.Operator):
    bl_idname = 'sna.gcode_import'
    bl_label = 'G-code → Curves'
    bl_description = ('Import sliced G-code as curve objects with a round bevel profile. '
                      'Colors come from the file palette (filament_colour) or from the tool list')
    bl_options = {'REGISTER', 'UNDO'}

    keep_walls: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Walls (perimeters)', default=True)
    keep_surfaces: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Top / bottom surfaces', default=True)
    keep_infill: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Infill', default=True)
    keep_supports: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Supports', default=True)
    keep_skirt: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Skirt / Brim', default=False)
    keep_travel: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Travel moves', default=False,
        description='Non-extruding moves as thin curves — nozzle path preview, not printed geometry')
    skip_start: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Skip Start / End G-code', default=True,
        description='Drop extrusion before the first real ";TYPE:" comment and inside '
                    '";TYPE:Custom" blocks — the purge / prime line the printer lays down at '
                    'the bed edge. Ignored for files without feature comments, where start '
                    'gcode cannot be told apart from the model')
    simplify: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Simplify collinear points', default=True,
        description='Drop vertices that lie on a straight line. Usually removes 5-10x the geometry')
    simplify_angle: bpy.props.FloatProperty(
        update=_stash_gcode_settings, name='Simplify Angle', default=0.5, min=0.0, max=15.0,
        precision=2, subtype='ANGLE', unit='ROTATION',
        description='Points turning less than this stay on the line')
    width_mm: bpy.props.FloatProperty(
        update=_stash_gcode_settings, name='Line Width (mm)', default=0.0, min=0.0, max=5.0,
        precision=3,
        description='Extrusion width used for the tube diameter. 0 = take it from the file')
    bevel_resolution: bpy.props.IntProperty(
        update=_stash_gcode_settings, name='Profile Segments', default=2, min=0, max=6,
        description='Subdivisions of the round bevel. 2 = 8-gon. Lower is lighter to render')
    per_feature: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Object per Feature', default=True,
        description='Separate curve object per feature (walls / infill / supports). Off = one object per tool')
    replace_existing: bpy.props.BoolProperty(
        update=_stash_gcode_settings, name='Replace Previous Import', default=True,
        description='Delete the previous "GCODE Import" collection before building')

    _SPIN = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def invoke(self, context, event):
        sc = context.scene
        if not sc.sna_gcode_path:
            self.report({'ERROR'}, 'Pick a .gcode file first')
            return {'CANCELLED'}
        self._dialog_open = True
        _restore_gcode_settings(self, context)
        if not sc.sna_gcode_path or not os.path.exists(sc.sna_gcode_path):
            self.report({'ERROR'}, 'G-code file not found')
            return {'CANCELLED'}
        try:
            info = probe_gcode(sc.sna_gcode_path)
        except Exception as e:
            self.report({'ERROR'}, f'Cannot read gcode: {e}')
            return {'CANCELLED'}
        sc.sna_gcode_info = probe_summary(info)
        sc.sna_gcode_has_features = info['has_features']
        _fill_scene_colors(sc, info['tools'], info['colors'])
        self._probe = info
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        layout.label(text=os.path.basename(sc.sna_gcode_path), icon=_icon('FILE'))
        info = getattr(self, '_probe', None)
        if info:
            layout.label(text=probe_summary(info))
        if not sc.sna_gcode_has_features:
            layout.label(text='No ";TYPE:" comments in file — feature filters ignored',
                         icon=_icon('INFO'))
        col = layout.column(align=True)
        col.prop(self, 'keep_walls')
        col.prop(self, 'keep_surfaces')
        col.prop(self, 'keep_infill')
        col.prop(self, 'keep_supports')
        col.prop(self, 'keep_skirt')
        col.prop(self, 'keep_travel')
        col.prop(self, 'skip_start')
        col.separator()
        col.prop(self, 'simplify')
        if self.simplify:
            col.prop(self, 'simplify_angle')
        col.prop(self, 'width_mm')
        col.prop(self, 'bevel_resolution')
        col.prop(self, 'per_feature')
        col.prop(self, 'replace_existing')
        box = layout.box()
        box.label(text='Tool colors', icon=_icon('COLOR'))
        for i, item in enumerate(sc.sna_gcode_colors):
            box.prop(item, 'color', text=f'T{i}')

    def execute(self, context):
        _stash_gcode_settings(self, context)
        opts = {name: getattr(self, name) for name in _SNA_GCODE_PERSIST}
        opts['colors'] = [tuple(i.color) for i in context.scene.sna_gcode_colors]
        path = context.scene.sna_gcode_path
        self._log_lines = []
        self._gen = run_import(path, opts, log=self._log_lines.append)
        self._spin_idx = 0
        try:
            first = next(self._gen)
            self._apply_status(context, first)
        except StopIteration as stop:
            self._finish(context, stop.value)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f'{type(e).__name__}: {e}')
            return {'CANCELLED'}
        wm = context.window_manager
        wm.progress_begin(0, 100)
        self._timer = wm.event_timer_add(0.08, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            self._cleanup(context)
            self.report({'WARNING'}, 'G-code import cancelled')
            return {'CANCELLED'}
        if event.type == 'TIMER':
            try:
                self._apply_status(context, next(self._gen))
            except StopIteration as stop:
                self._cleanup(context)
                self._finish(context, stop.value)
                return {'FINISHED'}
            except Exception as e:
                print(f'[GCodeImport] FAILED: {type(e).__name__}: {e}', flush=True)
                self._cleanup(context)
                self.report({'ERROR'}, f'{type(e).__name__}: {e}')
                return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def _apply_status(self, context, status):
        text, pct = (status if isinstance(status, tuple) else (status, None))
        self._spin_idx = (self._spin_idx + 1) % len(self._SPIN)
        try:
            if context.workspace:
                context.workspace.status_text_set(
                    f'{self._SPIN[self._spin_idx]}  G-code import: {text}   (ESC to cancel)')
        except Exception:
            pass
        if pct is not None:
            try:
                context.window_manager.progress_update(max(0, min(100, int(pct))))
            except Exception:
                pass

    def _cleanup(self, context):
        wm = context.window_manager
        if getattr(self, '_timer', None) is not None:
            try:
                wm.event_timer_remove(self._timer)
            except Exception:
                pass
            self._timer = None
        try:
            wm.progress_end()
        except Exception:
            pass
        try:
            if context.workspace:
                context.workspace.status_text_set(None)
        except Exception:
            pass

    def _finish(self, context, summary):
        for line in getattr(self, '_log_lines', []):
            print(f'[GCodeImport] {line}', flush=True)
        if not summary:
            self.report({'WARNING'}, 'Nothing imported')
            return
        self.report({'INFO'},
                    f'{summary["objects"]} objects, {_compact(summary["splines"])} splines, '
                    f'tube {summary["bevel_depth"] * 1000:.3f} mm')
        context.scene.sna_gcode_info = (
            f'{summary["objects"]} objects · {_compact(summary["splines"])} splines')


# --------------------------------------------------------------------------- self test

def _self_test_gcode():
    """Synthetic Orca-style file: 2 tools, absolute+relative E, an arc, retraction,
    travel, every feature bucket, and a config block with a 2-color palette."""
    return '\n'.join([
        '; HEADER_BLOCK_START',
        '; generated by OrcaSlicer 2.1.0 (self-test)',
        '; HEADER_BLOCK_END',
        'M83',
        'G90',
        'M104 S210 T0',
        'M104 S200 T1',
        'T0',
        ';TYPE:Outer wall',
        'G1 X0 Y0 Z0.2 E0.5',
        'G1 X20 Y0 Z0.2 E0.5',
        ';TYPE:Inner wall',
        'G1 X20 Y5 Z0.2 E0.5',
        'G1 X0 Y5 Z0.2 E0.5',
        ';TYPE:Sparse infill',
        'G1 X0 Y10 Z0.2 E0.5',
        'G1 X20 Y10 Z0.2 E0.5',
        ';TYPE:Support',
        'G1 X0 Y15 Z0.2 E0.5',
        'G1 X20 Y15 Z0.2 E0.5',
        ';TYPE:Skirt',
        'G1 X-2 Y-2 Z0.2 E0.5',
        'G1 X22 Y-2 Z0.2 E0.5',
        'T1',
        ';TYPE:Top surface',
        'M82',
        'G1 X0 Y20 Z0.2 E10.0',
        'G1 X20 Y20 Z0.2 E20.0',
        'G1 X20 Y20 Z2.0 E20.0 F6000',   # travel-like Z move, no extrusion
        'G1 X20 Y20 Z2.0 E19.5',          # retract: negative delta, must be ignored
        'G3 X40 Y20 Z2.0 I10 J0 E20.5',   # arc, ccw quarter
        '; no TYPE here, still T1',
        'G1 X60 Y20 Z2.0 E21.5',
        '; CONFIG_BLOCK at the end, as Orca writes it when verbose gcode is on',
        '; filament_colour = #FF8000;#008000',
        '; filament_type = PLA;PETG',
        '; line_width = 0.42',
        '',
    ])


class SNA_OT_test_gcode_import(bpy.types.Operator):
    bl_idname = 'sna.test_gcode_import'
    bl_label = 'Self-Test: G-code Import'
    bl_description = ('Writes a synthetic Orca-style gcode, runs the probe and the full '
                      'import, and checks tools, buckets, palette and curve output')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base = 'F:/' if os.path.isdir('F:/') else context.preferences.filepaths.temporary_directory
        if not base or not os.path.isdir(base):
            base = os.path.expanduser('~')
        path = os.path.join(base, '_ebc_gcode_selftest.gcode')
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(_self_test_gcode())

        fails = []
        try:
            info = probe_gcode(path)
            if info['tools'] != [0, 1]:
                fails.append(f'tools {info["tools"]} != [0, 1]')
            if info['colors'] != ['FF8000', '008000']:
                fails.append(f'colors {info["colors"]}')
            if not info['has_features']:
                fails.append('features not detected')

            parsed = _drain(parse_gcode(path))
            if not parsed['has_features']:
                fails.append('parser missed ;TYPE:')
            buckets = {k[1] for k in parsed['paths']}
            for want in ('walls', 'infill', 'supports', 'skirt', 'surfaces'):
                if want not in buckets:
                    fails.append(f'bucket {want} missing (have {sorted(buckets)})')
            if parsed['tools'] != [0, 1]:
                fails.append(f'parsed tools {parsed["tools"]}')
            if parsed['n_arcs'] != 1:
                fails.append(f'arcs {parsed["n_arcs"]}')
            # retraction must not extend a path: total points are those of real moves
            pts = parsed['n_points']
            if pts < 10:
                fails.append(f'too few points ({pts})')

            opts = {
                'keep_walls': True, 'keep_surfaces': True, 'keep_infill': True,
                'keep_supports': True, 'keep_skirt': False, 'keep_travel': False,
                'skip_start': True, 'simplify': True, 'simplify_angle': 0.5, 'width_mm': 0.4,
                'bevel_resolution': 2, 'per_feature': True, 'replace_existing': True,
                'colors': [hex_to_rgba('#FF8000'), hex_to_rgba('#008000')],
            }
            summary = _drain(run_import(path, opts))
            if summary['objects'] < 4:
                fails.append(f'objects {summary["objects"]}')
            if abs(summary['bevel_depth'] - 0.4 * MM * 0.5) > 1e-9:
                fails.append(f'bevel {summary["bevel_depth"]}')
            mat = bpy.data.materials.get('EBC_GCODE_T0')
            if mat is None:
                fails.append('material EBC_GCODE_T0 missing')
            else:
                node = mat.node_tree.nodes.get('Principled BSDF')
                got = tuple(node.inputs['Base Color'].default_value)[:3]
                want = hex_to_rgba('#FF8000')[:3]
                if max(abs(a - b) for a, b in zip(got, want)) > 1e-5:
                    fails.append(f'material color {got} != {want}')
            coll = bpy.data.collections.get(COLL_NAME)
            names = sorted(o.name for o in coll.objects) if coll else []
            if not any(n.startswith('GCODE_T1') for n in names):
                fails.append(f'no T1 object in {names}')
        finally:
            coll = bpy.data.collections.get(COLL_NAME)
            if coll is not None:
                for ob in list(coll.objects):
                    data = ob.data
                    bpy.data.objects.remove(ob, do_unlink=True)
                    if data is not None and data.users == 0:
                        bpy.data.curves.remove(data)
                bpy.data.collections.remove(coll)
            for tool in (0, 1):
                mat = bpy.data.materials.get(f'EBC_GCODE_T{tool}')
                if mat is not None and mat.users == 0:
                    bpy.data.materials.remove(mat)
            try:
                os.remove(path)
            except OSError:
                pass

        if fails:
            msg = '; '.join(fails)
            print(f'[GCodeImport][TEST] FAIL: {msg}', flush=True)
            self.report({'ERROR'}, f'Self-test failed: {msg}')
            return {'CANCELLED'}
        print('[GCodeImport][TEST] PASS — probe, parser, buckets, arc, palette, curves, material',
              flush=True)
        self.report({'INFO'}, 'Self-test passed: probe, parser, buckets, arc, palette, curves')
        return {'FINISHED'}


def sna_gcode_import_interface(layout):
    box = layout.box()
    box.label(text='G-code → Curves (Orca)', icon=_icon('CURVE_DATA'))
    sc = bpy.context.scene
    row = box.row(align=True)
    row.prop(sc, 'sna_gcode_path', text='')
    row.operator('sna.gcode_browse', text='', icon=_icon('FILEBROWSER'))
    if sc.sna_gcode_info:
        box.label(text=sc.sna_gcode_info, icon=0)
    col = box.column()
    col.enabled = bool(sc.sna_gcode_path)
    col.operator('sna.gcode_import', text='Import as Curves', icon=_icon('CURVE_DATA'))
    box.operator('sna.test_gcode_import', text='Self-Test: G-code Import',
                 icon=_icon('EXPERIMENTAL'))


# --------------------------------------------------------------------------- registration

_classes = (
    SNA_GcodeColor,
    SNA_OT_gcode_browse,
    SNA_OT_gcode_import,
    SNA_OT_test_gcode_import,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sna_gcode_path = bpy.props.StringProperty(
        name='G-code File', subtype='FILE_PATH', default='',
        description='Sliced .gcode to import as curves')
    bpy.types.Scene.sna_gcode_info = bpy.props.StringProperty(
        name='G-code Info', default='')
    bpy.types.Scene.sna_gcode_has_features = bpy.props.BoolProperty(
        name='Has Feature Comments', default=False)
    bpy.types.Scene.sna_gcode_colors = bpy.props.CollectionProperty(type=SNA_GcodeColor)
    bpy.types.Scene.sna_gcode_colors_index = bpy.props.IntProperty(default=0)


def unregister():
    del bpy.types.Scene.sna_gcode_colors_index
    del bpy.types.Scene.sna_gcode_colors
    del bpy.types.Scene.sna_gcode_has_features
    del bpy.types.Scene.sna_gcode_info
    del bpy.types.Scene.sna_gcode_path
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
