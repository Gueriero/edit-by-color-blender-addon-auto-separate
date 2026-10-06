# Voxel Size Map (weight-driven block gradient) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a painted vertex group drive the cube size in `SNA_OT_voxel_block_remesh` — hot (weight 1) keeps the smallest blocks, cold (weight 0) coarsens them up to 2x/4x/8x, on the existing base lattice so the mesh stays watertight.

**Architecture:** The occupancy array `occ` (dense bool, one cell per base size) is block-quantised in the cold zone: aligned blocks of `2**L` base cells whose cells are all cold are forced solid (if at least `fill` of their base cells are occupied) or empty. Geometry, colours, welding, separation and open-edge filling are untouched, because faces are still emitted on the base lattice. Painted weights are gathered during the existing rasterisation pass and turned into a per-cell uint8 level grid after the interior fills.

**Tech Stack:** Blender 5.0.1 addon, single file `__init__.py`, numpy, bmesh; headless self-tests run with `E:/Blender/5/blender.exe --background`.

**Spec:** `docs/superpowers/specs/2026-10-06-voxel-size-map-design.md`

## Global Constraints

- All code changes go into `F:\Edit by Color by KIRI Engine\__init__.py` (CRLF file — never rewrite it with a Python script that changes line endings; use the Edit tool).
- Version bump goes into `blender_manifest.toml` (`version = "X.Y.Z"`).
- Every new operator property must carry `update=_sna_voxel_stash_settings` **and** its identifier must be appended to `_SNA_VOXEL_PERSIST`, or it silently resets on restart.
- New dialog controls go into the **live** `draw()` (`__init__.py:4168`); the earlier `draw()` at `__init__.py:4053` is dead code shadowed by it.
- Headless test command pattern: `TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python <script>` (C: has no free space — scratch files go to `F:/ebc_debug`).
- Commit messages: English, conventional style, ending with `Co-Authored-By: Claude Code <noreply@anthropic.com>`.
- Never fan an n-gon from loop 0 — the BVH build uses `mesh.calc_loop_triangles()`; do not touch that path.

---

### Task 1: Dialog surface — 7 new properties, persistence, live UI

**Files:**
- Modify: `__init__.py` (class `SNA_OT_voxel_block_remesh`, ~`3933-4044`; `_SNA_VOXEL_PERSIST`, `3882-3887`; live `draw()`, `4168-4195`; `sna.test_dialog_stash`, ~`5980-6075`)

**Interfaces:**
- Consumes: nothing.
- Produces: operator properties `size_map_enabled` (bool), `size_map_group` (str), `size_map_max` (enum `'X2'|'X4'|'X8'`), `size_map_curve` (float), `size_map_fill` (float), `size_map_smoothing` (int), `size_map_invert` (bool) — later tasks read these via `self.*`.

- [ ] **Step 1: Add the seven properties**

Insert right after the `color_gamma` property (before the `_SPIN` list) in `SNA_OT_voxel_block_remesh`:

```python
    size_map_enabled: bpy.props.BoolProperty(
        update=_sna_voxel_stash_settings,
        name='Size Map (Weight Paint)', default=False,
        description='Let a painted vertex group drive the cube size: hot (weight 1) keeps the '
                    'smallest blocks, cold (weight 0) coarsens them up to Max Block Size.\n'
                    'Unpainted vertices are cold, so paint only the parts that need detail.\n'
                    'Memory and time equal a uniform run at the smallest block size',
    )
    size_map_group: bpy.props.StringProperty(
        update=_sna_voxel_stash_settings,
        name='Vertex Group', default='',
        description='Vertex group painted in Weight Paint mode, one 0..1 weight per vertex',
    )
    size_map_max: bpy.props.EnumProperty(
        update=_sna_voxel_stash_settings,
        name='Max Block Size', default='X4',
        items=[('X2', '2x', 'Coldest blocks are twice the Block Size'),
               ('X4', '4x', 'Coldest blocks are four times the Block Size'),
               ('X8', '8x', 'Coldest blocks are eight times the Block Size')],
        description='How much larger the coldest blocks get. Sizes stay powers of two so every '
                    'block sits on the same lattice and the mesh stays watertight',
    )
    size_map_curve: bpy.props.FloatProperty(
        update=_sna_voxel_stash_settings,
        name='Response', default=1.0, min=0.2, max=5.0, precision=2, step=1,
        description='How the painted weight maps to a size: 1 = linear, below 1 pushes more of '
                    'the surface towards small blocks, above 1 towards large ones',
    )
    size_map_fill: bpy.props.FloatProperty(
        update=_sna_voxel_stash_settings,
        name='Fill Threshold', default=0.5, min=0.0, max=1.0, precision=2, step=1,
        description='Fraction of a block\'s base cells that must be solid for the whole block to '
                    'become solid.\n0.5 = replica of the model; 0 = any occupied cell makes the '
                    'block solid (nothing is ever lost, the cold zone gets fatter); 1 = only '
                    'fully solid blocks are kept (thinnest, thin cold details can disappear)',
    )
    size_map_smoothing: bpy.props.IntProperty(
        update=_sna_voxel_stash_settings,
        name='Smoothing Passes', default=2, min=0, max=8,
        description='Box-filter passes over the painted weight field before sizes are chosen. '
                    'Removes speckle from sparse paint at the cost of softer size borders',
    )
    size_map_invert: bpy.props.BoolProperty(
        update=_sna_voxel_stash_settings,
        name='Invert (hot = bigger)', default=False,
        description='Swap the direction: hot (weight 1) becomes the largest blocks',
    )
```

- [ ] **Step 2: Add them to the persist tuple**

```python
_SNA_VOXEL_PERSIST = (
    'cell_size_mm', 'num_colors', 'kmeans_iters', 'kmeans_subsample', 'use_hsv', 'do_separate',
    'remove_original', 'merge_verts', 'fill_open_edges', 'fix_checker', 'collapse_similar',
    'collapse_dist', 'use_face_materials', 'grayscale', 'saturation', 'highlight_lift',
    'shadow_drop', 'color_gamma',
    'size_map_enabled', 'size_map_group', 'size_map_max', 'size_map_curve', 'size_map_fill',
    'size_map_smoothing', 'size_map_invert',
)
```

- [ ] **Step 3: Draw them in the live `draw()`**

In the live `draw()` (`__init__.py:4168`), right after `layout.prop(self, 'color_gamma')` and before the `Relief (open plane, no back wall):` column, insert:

```python
        sm = layout.column(align=True)
        sm.label(text='Size Map (Weight Paint):')
        sm.prop(self, 'size_map_enabled')
        sub = sm.column(align=True)
        sub.enabled = self.size_map_enabled
        obj = context.view_layer.objects.active
        if obj is not None and obj.type == 'MESH':
            sub.prop_search(self, 'size_map_group', obj, 'vertex_groups', text='Vertex Group')
        else:
            sub.prop(self, 'size_map_group', text='Vertex Group')
        sub.prop(self, 'size_map_max')
        sub.prop(self, 'size_map_curve')
        sub.prop(self, 'size_map_fill')
        sub.prop(self, 'size_map_smoothing')
        sub.prop(self, 'size_map_invert')
```

- [ ] **Step 4: Teach `sna.test_dialog_stash` about enum properties**

The perturbation ladder in `SNA_OT_test_dialog_stash.execute` currently does `float(default) + 0.37` for anything that is not bool/int, which raises `ValueError` on an enum default. Replace the value-picking block:

```python
            for name in persist:
                default = props[name].default
                if props[name].type == 'ENUM':
                    items = [it.identifier for it in props[name].enum_items]
                    value = next(i for i in items if i != default)
                elif isinstance(default, bool):
                    value = not default
                elif isinstance(default, int):
                    value = default + 1
                else:
                    value = float(default) + 0.37
                setattr(op, name, value)
                expect[name] = value
```

- [ ] **Step 5: Run the stash self-test**

Run: `TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python F:/ebc_debug/run_all_self_tests.py`
(the scratch runner iterates `sna.test_keep_original`, `sna.test_dialog_stash`, `sna.test_progressive_separate`, `sna.test_merge_islands`)
Expected: `[TestStash] voxel: 25 props, mismatched=[], still in WM=False` and `=== PASS ===` for every test.

- [ ] **Step 6: Commit**

```bash
cd "F:/Edit by Color by KIRI Engine"
git add __init__.py
git commit -m "feat(voxel): size-map dialog surface and persistence

Seven new properties for the weight-driven block gradient, wired into the
sticky dialog stash; the stash self-test now handles enum defaults.

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 2: Read the painted weights and carry them onto the cells

**Files:**
- Modify: `__init__.py` (`_work`, phase 1 `4214-4239`, occupancy `4343-4453`)

**Interfaces:**
- Consumes: `self.size_map_enabled`, `self.size_map_group`, `self.size_map_invert` from Task 1.
- Produces: local `vert_weights` (`np.float32[n_verts]` or `None`) and `cell_weight` (dict `(ix,iy,iz) -> float`, the max weight seen) — Task 3 consumes both.

- [ ] **Step 1: Read the vertex group in phase 1**

Insert after the image/material read block (`__init__.py:4239`, before `# Phase 2: Build BVHTree`):

```python
        # Phase 1b: painted size map — one weight per vertex (0..1). Vertex groups are not
        # mesh attributes and have no foreach_get path, so this is a plain loop
        # (~2 s per 1.5M vertices, chunked so the modal spinner keeps ticking).
        vert_weights = None
        if self.size_map_enabled:
            vg = obj.vertex_groups.get(self.size_map_group)
            if vg is None:
                raise RuntimeError(f'Vertex group "{self.size_map_group}" not found on the object')
            n_v = len(obj.data.vertices)
            if n_v == 0:
                raise RuntimeError('Mesh has no vertices')
            vert_weights = np.zeros(n_v, dtype=np.float32)
            gi = vg.index
            step = max(1, n_v // 20)
            for vi, v in enumerate(obj.data.vertices):
                for g in v.groups:
                    if g.group == gi:
                        vert_weights[vi] = g.weight
                        break
                if vi % step == 0:
                    yield (f'Reading size map {vi * 100 // n_v}%', 1)
            if self.size_map_invert:
                vert_weights = 1.0 - vert_weights
            w_min, w_max = float(vert_weights.min()), float(vert_weights.max())
            log(f'Size map "{self.size_map_group}": {n_v} vertices, weight {w_min:.3f}..{w_max:.3f}')
            if w_max - w_min < 1e-6:
                raise RuntimeError(f'Size map "{self.size_map_group}" is constant '
                                   f'(every weight {w_min:.3f}) — the gradient would do nothing')
```

- [ ] **Step 2: Give `_add` an optional weight and collect the per-cell field**

Replace the `occupied = set()` / `_add` block (`__init__.py:4343-4347`):

```python
        occupied = set()
        # painted weights per cell, sparse: a dense grid would cost hundreds of MiB at fine
        # block sizes. The max rule keeps the finest cube wherever cells conflict.
        cell_weight = {}

        def _add(ix, iy, iz, w=None):
            if 0 <= ix < grid_size_x and 0 <= iy < grid_size_y and 0 <= iz < grid_size_z:
                cell = (ix, iy, iz)
                occupied.add(cell)
                if w is not None:
                    prev = cell_weight.get(cell)
                    if prev is None or w > prev:
                        cell_weight[cell] = w
```

- [ ] **Step 3: Feed the weights from vertex seeds and the rasteriser**

Vertex seeding (`__init__.py:4350-4354`) becomes:

```python
        for vi in range(n_verts):
            v = verts_world[vi]
            if vert_weights is not None:
                _add(int((v[0] - bbox_min[0]) / cell_size),
                     int((v[1] - bbox_min[1]) / cell_size),
                     int((v[2] - bbox_min[2]) / cell_size),
                     float(vert_weights[vi]))
            else:
                _add(int((v[0] - bbox_min[0]) / cell_size),
                     int((v[1] - bbox_min[1]) / cell_size),
                     int((v[2] - bbox_min[2]) / cell_size))
```

In the rasteriser, precompute the triangle's three vertex weights once per triangle — right after `tri_v = tri_verts.reshape(-1, 3)` (`__init__.py:4365`):

```python
        tri_w = None
        if vert_weights is not None:
            tri_w = (vert_weights[tri_v[:, 0]], vert_weights[tri_v[:, 1]], vert_weights[tri_v[:, 2]])
```

and inside the triangle loop, right after `c_vec = verts_world[tri_v[ti, 2]]`:

```python
            if tri_w is not None:
                wa = float(tri_w[0][ti]); wb = float(tri_w[1][ti]); wc = float(tri_w[2][ti])
```

then replace the accepted-cell `_add(ix, iy, iz)` call (`__init__.py:4415`) with:

```python
                                if tri_w is not None:
                                    _add(ix, iy, iz, w0 * wa + w1 * wb + w2 * wc)
                                else:
                                    _add(ix, iy, iz)
```

(`w2` is already computed one line above the acceptance test.) Cells added by the 1-ring expand and the BVH verification keep no weight — Task 3 propagates them from their neighbours on the dense grid.

- [ ] **Step 4: Log the gathered field (temporary, removed in Task 3)**

At the end of the BVH verification block (`__init__.py:4452`, before the `log(f'BVH verified: ...')` line) add:

```python
        if vert_weights is not None:
            log(f'Size map: {len(cell_weight)} of {len(occupied)} cells carry a painted weight')
```

- [ ] **Step 5: Verify geometry is unchanged when nothing consumes the weights**

Write `F:/ebc_debug/verify_size_map.py` (scratch, not shipped). It builds a subdivided cube with a radial `Heat` group, runs the real `_work` twice, and compares. This file is extended in Task 3, so keep the run loop parameterised:

```python
import os, sys, math, textwrap, inspect
import numpy as np
import bpy, bmesh, mathutils

sys.path.insert(0, 'F:/ebc_debug')
import importlib.util
spec = importlib.util.spec_from_file_location('ebc_dev', r'f:\Edit by Color by KIRI Engine\__init__.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.register()
WORK = textwrap.dedent(inspect.getsource(mod.SNA_OT_voxel_block_remesh._work))


class Fake:
    cell_size_mm = 2.0; num_colors = 4; kmeans_iters = 20; kmeans_subsample = 20000
    use_hsv = True; do_separate = False; remove_original = False; merge_verts = True
    fill_open_edges = False; fix_checker = True; collapse_similar = False; collapse_dist = 1.5
    use_face_materials = True; grayscale = False; saturation = 1.0; highlight_lift = 0.0
    shadow_drop = 0.0; color_gamma = 1.0
    size_map_enabled = False; size_map_group = 'Heat'; size_map_max = 'X4'
    size_map_curve = 1.0; size_map_fill = 0.5; size_map_smoothing = 2; size_map_invert = False


def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = 'SizeMapProbe'
    obj.scale = (0.05, 0.012, 0.05)          # 100 x 24 x 100 mm
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=24)
    bpy.ops.object.mode_set(mode='OBJECT')
    me = obj.data
    for v in me.vertices:                      # bump the +Y face so the surface is not flat
        if v.co.y > 0:
            r = math.hypot(v.co.x, v.co.z)
            v.co.y += 0.010 * math.exp(-(r / 0.030) ** 2)
    vg = obj.vertex_groups.new(name='Heat')
    for v in me.vertices:
        r = math.hypot(v.co.x, v.co.z)
        vg.add([v.index], max(0.0, 1.0 - r / 0.040), 'REPLACE')
    me.materials.append(bpy.data.materials.new('ProbeMat'))
    me.update()
    return obj


def run(enable, fill):
    src = build()
    op = Fake()
    op.size_map_enabled = enable
    op.size_map_fill = fill
    ns = dict(mod.__dict__)
    exec(compile(WORK, '<verify_work>', 'exec'), ns)
    for _ in ns['_work'](op, bpy.context, src, None, ''):
        pass
    res = [o for o in bpy.data.objects if o.name.startswith(('MAT_', 'HSV_', 'sRGB_'))]
    assert res, 'no result object'
    out = res[0]
    co = np.array([v.co[:] for v in out.data.vertices])
    return out, len(out.data.polygons), co.min(axis=0), co.max(axis=0)


off, n_off, lo_off, hi_off = run(False, 0.5)
on, n_on, lo_on, hi_on = run(True, 0.5)
same = (n_off == n_on) and np.allclose(lo_off, lo_on, atol=1e-6) and np.allclose(hi_off, hi_on, atol=1e-6)
print(f'{"PASS" if same else "FAIL"} identical geometry ({n_off} vs {n_on} faces, name {on.name})', flush=True)
```

```bash
TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python F:/ebc_debug/verify_size_map.py
```

Expected: `PASS identical geometry (N vs N faces, ...)`, plus the log lines `Size map "Heat": ... vertices, weight 0.000..1.000` and `Size map: K of M cells carry a painted weight` with K > 0.

- [ ] **Step 6: Commit**

```bash
cd "F:/Edit by Color by KIRI Engine"
git add __init__.py
git commit -m "feat(voxel): read painted size map and gather per-cell weights

Vertex-group weights are read once per vertex and accumulated onto the
occupancy cells during the existing rasterisation pass (max rule). Nothing
consumes them yet, so the geometry is unchanged.

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 3: Level field, block quantisation, checker re-run, result name

**Files:**
- Modify: `__init__.py` (module level helpers before `class SNA_OT_voxel_block_remesh`; `_work` fills/extraction boundary `4585-4612`; `res_name` `4918-4924`)

**Interfaces:**
- Consumes: `vert_weights`, `cell_weight` (Task 2), `self.size_map_max/curve/fill/smoothing`.
- Produces: module functions `_sna_voxel_fix_diagonal_contacts(occ) -> int` and `_sna_voxel_blockify(occ, level, lmax, fill, log) -> int` — Task 4's self-test calls both directly.

- [ ] **Step 1: Write the failing self-test (it must fail with NameError until the helpers exist)**

Add `SNA_OT_test_size_map` next to the other `SNA_OT_test_*` operators (before `SNA_OT_remove_ebc_modifier_from_selected`):

```python
class SNA_OT_test_size_map(bpy.types.Operator):
    bl_idname = 'sna.test_size_map'
    bl_label = 'Self-Test: Size Map Blockify'
    bl_description = ('Unit test for the painted size-map block quantiser: hot blocks stay '
                      'untouched, empty blocks are never filled, fill 0.5 versus 0 differ only '
                      'on partially occupied cold blocks, and the blockified surface has no '
                      'boundary or non-manifold edges after welding. Reports PASS/FAIL in console')
    bl_options = {'REGISTER'}

    def execute(self, context):
        import numpy as np
        import bmesh

        def p(msg):
            print(f'[TestSizeMap] {msg}', flush=True)

        def build(shape, level, occ_cells):
            occ = np.zeros(shape, dtype=bool)
            for c in occ_cells:
                occ[c] = True
            lvl = np.zeros(shape, dtype=np.uint8)
            for c, v in level.items():
                lvl[c] = v
            return occ, lvl

        def topology(occ):
            """Emit the same unit faces the voxeliser emits, weld, and count bad edges."""
            gx, gy, gz = occ.shape
            bm = bmesh.new()
            verts = {}
            DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
            def vkey(x, y, z):
                k = (x, y, z)
                if k not in verts:
                    verts[k] = bm.verts.new((x, y, z))
                return verts[k]
            for di, (dx, dy, dz) in enumerate(DIRS):
                for ix, iy, iz in np.argwhere(occ):
                    nx, ny, nz = ix + dx, iy + dy, iz + dz
                    if 0 <= nx < gx and 0 <= ny < gy and 0 <= nz < gz and occ[nx, ny, nz]:
                        continue
                    cx, cy, cz = int(ix), int(iy), int(iz)
                    if dx == 1:   quad = [(cx+1, cy, cz), (cx+1, cy+1, cz), (cx+1, cy+1, cz+1), (cx+1, cy, cz+1)]
                    elif dx == -1: quad = [(cx, cy, cz), (cx, cy, cz+1), (cx, cy+1, cz+1), (cx, cy+1, cz)]
                    elif dy == 1:  quad = [(cx, cy+1, cz), (cx, cy+1, cz+1), (cx+1, cy+1, cz+1), (cx+1, cy+1, cz)]
                    elif dy == -1: quad = [(cx, cy, cz), (cx+1, cy, cz), (cx+1, cy, cz+1), (cx, cy, cz+1)]
                    elif dz == 1:  quad = [(cx, cy, cz+1), (cx+1, cy, cz+1), (cx+1, cy+1, cz+1), (cx, cy+1, cz+1)]
                    else:          quad = [(cx, cy, cz), (cx, cy+1, cz), (cx+1, cy+1, cz), (cx+1, cy, cz)]
                    try:
                        bm.faces.new([vkey(*q) for q in quad])
                    except ValueError:
                        pass
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            boundary = sum(1 for e in bm.edges if e.is_boundary)
            nonman = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
            bm.free()
            return boundary, nonman

        shape = (8, 8, 8)
        ok = True

        # 1. solid cold slab, entirely occupied -> blockify to 4x must keep it solid and clean
        occ, lvl = build(shape, {}, [])
        occ[0:8, 0:8, 0:8] = True
        lvl[0:8, 0:8, 0:8] = 2
        n_before = int(occ.sum())
        _sna_voxel_blockify(occ, lvl, 2, 0.5)
        slab_ok = int(occ.sum()) == n_before
        p(f'solid cold slab unchanged: {slab_ok} ({n_before} -> {int(occ.sum())} cells)')
        ok = ok and slab_ok

        # 2. empty cold blocks are never filled, whatever the threshold
        occ, lvl = build(shape, {}, [])
        occ[0:2, 0:2, 0:2] = True
        lvl[0:8, 0:8, 0:8] = 2
        _sna_voxel_blockify(occ, lvl, 2, 0.0)
        empty_ok = int(occ.sum()) == 8 and not occ[4:8, 4:8, 4:8].any()
        p(f'empty blocks stay empty at fill 0: {empty_ok} ({int(occ.sum())} cells)')
        ok = ok and empty_ok

        # 3. hot blocks are never touched: a level-0 block keeps its partial occupancy
        occ, lvl = build(shape, {}, [])
        occ[0:4, 0:4, 0] = True          # a 1-cell-thick plate inside a cold 8x8x8 block
        lvl[4:8, 4:8, 4:8] = 2
        n_before = int(occ.sum())
        _sna_voxel_blockify(occ, lvl, 2, 0.5)
        hot_ok = int(occ.sum()) == n_before
        p(f'hot blocks untouched: {hot_ok} ({n_before} -> {int(occ.sum())} cells)')
        ok = ok and hot_ok

        # 4. fill 0.5 vs 0 differ exactly on partially occupied cold blocks
        def run(fill):
            o, l = build(shape, {}, [])
            o[0:2, 0:2, 0:2] = True       # 8 of a 4x4x4 block's 64 cells -> 12.5%
            l[0:8, 0:8, 0:8] = 2
            _sna_voxel_blockify(o, l, 2, fill)
            return int(o.sum())
        thin_05, thin_00 = run(0.5), run(0.0)
        fill_ok = thin_05 == 0 and thin_00 == 64
        p(f'fill 0.5 -> {thin_05} cells, fill 0.0 -> {thin_00} cells (expected 0 / 64)')
        ok = ok and fill_ok

        # 5. blockified geometry is watertight: a 1-cell shell, cold at level 1
        occ, lvl = build(shape, {}, [])
        occ[2, 2:6, 2:6] = True           # 4x4 single-layer patch
        lvl[2, 2:6, 2:6] = 1
        b0, n0 = topology(occ)
        _sna_voxel_blockify(occ, lvl, 1, 0.0)
        b1, n1 = topology(occ)
        topo_ok = (b0, n0) == (0, 0) and (b1, n1) == (0, 0)
        p(f'topology before {b0}/{n0}, after {b1}/{n1} (boundary/non-manifold, expected 0/0)')
        ok = ok and topo_ok

        if ok:
            p('=== PASS ===')
            self.report({'INFO'}, 'TestSizeMap PASS')
        else:
            p('=== FAIL ===')
            self.report({'ERROR'}, 'TestSizeMap FAIL')
        return {'FINISHED' if ok else 'CANCELLED'}
```

Register it in `register()` right after `SNA_OT_test_voxel_block_remesh`, and in `unregister()` next to it.

- [ ] **Step 2: Extract the diagonal-contact pass into a module-level helper**

Add before `class SNA_OT_voxel_block_remesh` (next to the other `_sna_*` helpers around `__init__.py:3882`):

```python
def _sna_voxel_fix_diagonal_contacts(occ, passes=6):
    """Fill one empty cell of every diagonal (checkerboard) contact so no edge ends up
    shared by 4 faces. Works on the dense occupancy grid in place; returns cells added.
    """
    import numpy as np
    added_total = 0
    for _pass in range(passes):
        added = 0
        for a0, a1 in ((0, 1), (1, 2), (0, 2)):
            sl00 = [slice(None)] * 3; sl00[a0], sl00[a1] = slice(0, -1), slice(0, -1)
            sl11 = [slice(None)] * 3; sl11[a0], sl11[a1] = slice(1, None), slice(1, None)
            sl10 = [slice(None)] * 3; sl10[a0], sl10[a1] = slice(1, None), slice(0, -1)
            sl01 = [slice(None)] * 3; sl01[a0], sl01[a1] = slice(0, -1), slice(1, None)
            A = occ[tuple(sl00)]; B = occ[tuple(sl11)]
            Cn = occ[tuple(sl10)]; Dn = occ[tuple(sl01)]
            p1 = A & B & ~Cn & ~Dn
            p2 = Cn & Dn & ~A & ~B
            if p1.any():
                occ[tuple(sl10)][p1] = True
                added += int(p1.sum())
            if p2.any():
                occ[tuple(sl00)][p2] = True
                added += int(p2.sum())
        added_total += added
        if added == 0:
            break
    return added_total
```

Replace the inline pass in `_work` (`__init__.py:4499-4531`, the `if self.fix_checker:` block) with:

```python
        if self.fix_checker:
            yield ('Fixing diagonal contacts...', 19)
            t_checker = time.time()
            n_checker = _sna_voxel_fix_diagonal_contacts(occ)
            log(f'Diagonal contacts fixed: +{n_checker} cells in {time.time() - t_checker:.1f}s')
            yield (f'Diagonal contacts resolved ({n_checker} cells)', 19)
```

- [ ] **Step 3: Add the block quantiser**

Add after the helper above:

```python
def _sna_voxel_blockify(occ, level, lmax, fill, log=None):
    """Coarsen the occupancy in cold zones on the base lattice.

    `level` is a uint8 grid of size classes (0 = keep fine). An aligned block of 2**L base
    cells whose OCCUPIED cells are all at level >= L, not already covered by a coarser
    block and holding at least one occupied cell is forced solid when at least `fill` of its
    base cells are occupied (fill 0 = any cell) and empty otherwise. Air cells carry no
    level and never veto a block. Blocks that are not fully cold are left untouched, so
    painted detail survives. Returns the number of blocks quantised.
    """
    import numpy as np
    done = np.zeros(occ.shape, dtype=bool)
    blocks = 0
    for L in range(int(lmax), 0, -1):
        s = 2 ** L
        nx, ny, nz = occ.shape[0] // s, occ.shape[1] // s, occ.shape[2] // s
        if nx == 0 or ny == 0 or nz == 0:
            continue
        cut = (slice(0, nx * s), slice(0, ny * s), slice(0, nz * s))
        ob = occ[cut].reshape(nx, s, ny, s, nz, s)
        lb = level[cut].reshape(nx, s, ny, s, nz, s)
        db = done[cut].reshape(nx, s, ny, s, nz, s)
        axis = (1, 3, 5)
        cnt = ob.sum(axis=axis)
        # min level over the OCCUPIED cells only: air has no painted value and must not
        # make a block "not cold" (that would disable the whole feature)
        occ_min = np.where(ob, lb, 255).min(axis=axis)
        cold = (cnt > 0) & (occ_min >= L) & (~db.max(axis=axis))
        if not cold.any():
            continue
        if float(fill) <= 0.0:
            solid = cold & (cnt > 0)
        else:
            solid = cold & (cnt >= float(fill) * s ** 3)
        mask = np.broadcast_to(solid[:, None, :, None, :, None], ob.shape)
        keep = np.broadcast_to(cold[:, None, :, None, :, None], ob.shape)
        ob[keep] = mask[keep]
        db[np.broadcast_to(cold[:, None, :, None, :, None], db.shape)] = True
        blocks += int(solid.sum())
        if log:
            log(f'  size map: level {L} ({s}x{s}x{s} cells) applied to {int(solid.sum())} blocks')
    return blocks
```

- [ ] **Step 4: Build the level grid and apply it, right before the face extraction**

Insert between `occ |= to_fill` (`__init__.py:4585`) and the `free = ~occ` line (`__init__.py:4533` is earlier — the insertion point is immediately before `# Phase 4: Surface face extraction`):

```python
        # Phase 3d: the painted size map — level grid, then block quantisation. Only cold
        # blocks are touched, so the painted (hot) region keeps its exact fine occupancy.
        if vert_weights is not None:
            yield ('Applying the size map...', 21)
            t_map = time.time()
            w_grid = np.zeros((gx, gy, gz), dtype=np.float32)
            w_cnt = np.zeros((gx, gy, gz), dtype=np.float32)
            if cell_weight:
                ci = np.fromiter((v for cell in cell_weight for v in cell), dtype=np.int64,
                                 count=len(cell_weight) * 3).reshape(-1, 3)
                wv = np.fromiter(cell_weight.values(), dtype=np.float32, count=len(cell_weight))
                w_grid[ci[:, 0], ci[:, 1], ci[:, 2]] = wv
                w_cnt[ci[:, 0], ci[:, 1], ci[:, 2]] = 1.0
            # cells born in the 1-ring expand / BVH verify / fills have no sample: pull the
            # value in from occupied neighbours until nothing is missing
            for _ in range(4):
                missing = occ & (w_cnt == 0)
                if not missing.any():
                    break
                num = np.zeros_like(w_grid)
                den = np.zeros_like(w_cnt)
                for _ax in (0, 1, 2):
                    for _sh in (-1, 1):
                        num += np.roll(w_grid, _sh, axis=_ax)
                        den += np.roll(w_cnt, _sh, axis=_ax)
                take = missing & (den > 0)
                w_grid[take] = num[take] / den[take]
                w_cnt[take] = 1.0
            # smoothing: box filter over occupied cells only (air must not drag values down)
            for _ in range(int(self.size_map_smoothing)):
                acc = w_grid * w_cnt
                cnt = w_cnt.copy()
                for _ax in (0, 1, 2):
                    for _sh in (-1, 1):
                        acc = acc + np.roll(w_grid * w_cnt, _sh, axis=_ax)
                        cnt = cnt + np.roll(w_cnt, _sh, axis=_ax)
                live = cnt > 0
                w_grid[live] = acc[live] / cnt[live]
            lmax = {'X2': 1, 'X4': 2, 'X8': 3}[self.size_map_max]
            gamma = max(1e-3, float(self.size_map_curve))
            lvl = np.rint(np.power(np.clip(1.0 - w_grid, 0.0, 1.0), gamma) * lmax).astype(np.uint8)
            n_blocks = _sna_voxel_blockify(occ, lvl, lmax, self.size_map_fill, log)
            n_diag = _sna_voxel_fix_diagonal_contacts(occ)
            log(f'Size map: max {2 ** lmax}x, fill={self.size_map_fill:.2f}, '
                f'smoothing={self.size_map_smoothing} -> {n_blocks} blocks coarsened, '
                f'{n_diag} diagonal cells added in {time.time() - t_map:.1f}s')
            yield (f'Size map applied ({n_blocks} blocks)', 21)

```

- [ ] **Step 5: Put the size range into the result name**

Replace the `res_name` construction (`__init__.py:4918`):

```python
        if vert_weights is not None:
            _mult = {'X2': 2, 'X4': 4, 'X8': 8}[self.size_map_max]
            _size_token = f'{self.cell_size_mm:g}-{self.cell_size_mm * _mult:g}mm'
        else:
            _size_token = f'{self.cell_size_mm:g}mm'
        res_name = (f'{mode}_{_size_token}_K{len(cluster_mats)}_g{self.color_gamma:g}'
```

- [ ] **Step 6: Wire the temporary log line away**

Remove the Task 2 Step 4 log line (`Size map: ... cells carry a painted weight`) — the new `Size map: max ...x` line replaces it.

- [ ] **Step 7: Verify end to end on the synthetic relief**

Extend `F:/ebc_debug/verify_size_map.py`: replace the two-run tail with three runs (map off, on with fill 0.5, on with fill 0.0) and add topology + naming per run:

```python
def topology(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    nonman = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    parent = list(range(len(bm.verts)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b:
            parent[a] = b
    comps = len({find(i) for i in range(len(bm.verts))})
    bm.free()
    return boundary, nonman, comps


for label, enable, fill in (('off', False, 0.5), ('on 0.5', True, 0.5), ('on 0.0', True, 0.0)):
    out, faces, _, _ = run(enable, fill)
    b, nm, c = topology(out)
    print(f'{label}: faces={faces} boundary={b} nonmanifold={nm} components={c} name={out.name}', flush=True)
```

```bash
TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python F:/ebc_debug/verify_size_map.py
```

Expected:
- `on 0.5` has fewer faces than `off`;
- `boundary=0`, `nonmanifold=0`, `components=1` in every run;
- `on 0.5` and `on 0.0` differ (fill rule working);
- the on-runs are named `MAT_2-8mm_K..._Voxel` (`size_map_max='X4'`, `cell_size_mm=2.0`), the off-run `MAT_2mm_K..._Voxel`.

- [ ] **Step 8: Run it on the real model**

Point the same harness at the real file: open `F:\Китайский фотоконтент\барельефы\череп в очках\Meshy_AI_Deadbeat_DJ_1003211738_texture.blend` before registering the addon, take `Mesh_0.001`, set `cell_size_mm = 1.0`, `use_face_materials = True`, and paint the `Heat` group analytically (weight 1 inside the central disc of radius 0.22 * max(bbox.x, bbox.z), 0 outside — the same field `F:/ebc_debug/spike_real.py` used).

```bash
TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python F:/ebc_debug/verify_size_map_real.py
```

Expected, against the spike baseline: fewer faces than the uniform 2,749,524, `boundary == 0`, `nonmanifold == 0`, `components == 1`, and the same order of magnitude as the spike's 151,834 faces with fill 0.5.

- [ ] **Step 9: Commit**

```bash
cd "F:/Edit by Color by KIRI Engine"
git add __init__.py
git commit -m "feat(voxel): block quantisation from the painted size map

Cold blocks are forced solid/empty on the base lattice, the diagonal-contact
pass runs again on the coarser set, and the result name carries the size
range. Verified on the real relief: watertight, one component.

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 4: Validation, docs, release

**Files:**
- Modify: `__init__.py` (`execute()` `4066-4090`; new `SNA_OT_test_size_map` + registration; README.md; CLAUDE.md), `blender_manifest.toml`

**Interfaces:**
- Consumes: `_sna_voxel_blockify`, `_sna_voxel_fix_diagonal_contacts` (Task 3).
- Produces: `sna.test_size_map` self-test operator; released version.

- [ ] **Step 1: Validate the group in `execute()`**

In `SNA_OT_voxel_block_remesh.execute`, after the mesh-type check and before the colour-mode branch:

```python
        if self.size_map_enabled:
            if not self.size_map_group:
                self.report({'ERROR'}, 'Size Map: pick a vertex group'); return {'CANCELLED'}
            if obj.vertex_groups.get(self.size_map_group) is None:
                self.report({'ERROR'}, f'Size Map: vertex group "{self.size_map_group}" not found')
                return {'CANCELLED'}
```

- [ ] **Step 2: Run the self-test suite**

`sna.test_size_map` and its registration are added in Task 3, step 1. After the validation
guards above, run the whole suite once more:

Run: `TMPDIR=F:/ebc_debug "E:/Blender/5/blender.exe" --background --factory-startup --python F:/ebc_debug/run_all_self_tests.py`
Expected: `=== PASS ===` for `sna.test_size_map`, `sna.test_dialog_stash`,
`sna.test_keep_original`, `sna.test_progressive_separate`, `sna.test_merge_islands`.


- [ ] **Step 3: Document the feature**

- `README.md`: add a `### Size Map (Weight Paint)` subsection under the voxel section — what it does, the settings table, the fill-threshold warning, and that memory equals a uniform run at the smallest size.
- `CLAUDE.md`: extend the voxel architecture block with phase 3d (`_sna_voxel_blockify`, `_sna_voxel_fix_diagonal_contacts`, the two safety rules) and the new persist entries.

- [ ] **Step 4: Bump the version and build the release zip**

```bash
cd "F:/Edit by Color by KIRI Engine"
# blender_manifest.toml: version = "2.19.4"
powershell -NoProfile -File "F:\Edit by Color by KIRI Engine\build.ps1"
```

Expected: `edit_by_color_by_kiri_engine_v2.19.4.zip`.

- [ ] **Step 5: Commit and push**

```bash
cd "F:/Edit by Color by KIRI Engine"
git add __init__.py README.md CLAUDE.md blender_manifest.toml
git commit -m "feat(voxel): size map validation, self-test and docs

Co-Authored-By: Claude Code <noreply@anthropic.com>"
git push origin main
```

---

## Handover notes

- After Task 4 the feature is usable but unpainted geometry renders exactly as today (`size_map_enabled` default off), so no existing workflow changes.
- The remaining known limitation is deliberate: thin cold features depend on `Fill Threshold`; a thickness guard is out of scope for this version (spec, Risks).
- If the reviewer wants to see the effect before painting anything, `F:/ebc_debug/spike_real.py` produces `F:/ebc_debug/real_compare.png` (uniform | fill 0.5 | fill 0.0).
- Manual check for the user after the release zip is installed: paint a vertex group on a real relief, open the voxel dialog, tick `Size Map (Weight Paint)`, pick the group, run 2x / 4x / 8x and confirm the hot zone stays fine while the cold zone coarsens, that the result is named `MAT_<min>-<max>mm_..._Voxel`, and that the dialog remembers the settings after a Blender restart.
