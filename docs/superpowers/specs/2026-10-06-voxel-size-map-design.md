# Voxel Block Remesh — size gradient from a painted weight map

Date: 2026-10-06
Status: design, pending review
Applies to: `SNA_OT_voxel_block_remesh` in `__init__.py`

## Goal

Let the cube size vary across the model, driven by a painted vertex group: hot
(weight 1) = smallest cubes, cold (weight 0) = largest. Unpainted areas are cold,
so the user paints only the places that need detail. The result is a gradient of
block sizes over the surface — an artistic effect and, as a side effect, far fewer
faces in the coarse areas.

Not a performance feature: the voxel grid still runs at the finest size over the
whole bounding box, so memory and the early phases cost the same as a uniform run
at that size. What shrinks is everything downstream of the occupancy (colour
sampling, geometry, welding, separation) and the 200M-cell guard stays as it is.

## Non-goals

- No true adaptive/octree grid. Sizes are powers of two of `Block Size`
  (2x / 4x / 8x) so every block sits on the same lattice and the existing
  emitter stays valid.
- Colour handling is unchanged: faces keep their per-face texture/material
  sample, so a coarse block still carries fine colour detail. Nothing is
  averaged per block.
- Wall thickness, relief thickness and cap margins stay in base cells, which
  keeps their physical meaning because every base cell is still the same size.

## Design

The whole feature is a transformation of the occupancy array `occ` plus one new
per-cell field. Nothing in the emitter, colour path, k-means, welding,
separation or open-edge filling changes, because geometry is still emitted on
the base lattice: a coarse block is just a group of base cells that has been
forced solid or empty, and its surface is emitted as ordinary unit quads.

```
phase 1  read vertex group weights            -> vert_weights (n_verts,) float32
phase 3  raster / seed / verify / 1-ring      -> cell_weight  (sparse dict, max rule)
phase 3c densify + smooth + quantise          -> level grid (uint8, 0..L)
phase 3d blockify occ by level (cold only)    -> occ modified in place
phase 3e re-run the diagonal-contact fix      -> no new non-manifold contacts
phase 4+ unchanged                            -> faces, colours, weld, separate
```

### 1. Read the map

New code in phase 1 (next to the image/material colour read). A vertex group is
read with a plain per-vertex loop — verified in Blender 5.0.1 that vertex groups
are not mesh attributes and `foreach_get('groups', ...)` raises; the loop costs
about 2 s for 1.5M vertices, chunked with progress yields.

```python
vg = obj.vertex_groups.get(group_name)      # None if absent
w = np.zeros(len(me.vertices), dtype=np.float32)
gi = vg.index
for v in me.vertices:
    for g in v.groups:                       # vg.weight(i) raises for non-members
        if g.group == gi:
            w[v.index] = g.weight
```

Weights are 0..1 per group. Vertices outside the group stay 0 = coldest.

### 2. Per-cell weight, gathered where the cells are born

Everything happens in the existing occupancy phase, so no extra geometry queries:

- triangle rasterisation already has exact barycentric coordinates for each
  accepted cell (`__init__.py` raster inner loop) — accumulate
  `w0*Wa + w1*Wb + w2*Wc`;
- vertex seeding contributes its own vertex weight;
- 1-ring expand and BVH verification inherit the weight of the cell they came
  from (a verified cell takes the BVH hit triangle's weight);
- conflicts (a cell written by several triangles, or a seed and a raster hit)
  resolve by **max** — the finest cube wins, which is the conservative choice for
  detail.

Storage is a dict keyed by the cell tuple, mirroring `occupied`; a dense grid at
this point would cost hundreds of MiB at 0.26 mm (measured: 490 MiB float32 at a
128.4M-cell grid).

### 3. Densify, smooth, quantise

After the set -> dense handoff and after all fills, the weights are written into a
`uint8` grid (122.5 MiB at the 128.4M-cell worst case, measured). Then:

- **smoothing**: `Smoothing Passes` box filter over occupied cells only
  (weighted by occupancy so air does not drag values down). Kills speckle from
  sparse paint and from the max rule.
- **level**: `level = round((1 - w) ^ gamma * L)`, `L` = log2 of the max
  multiplier. `Invert` flips `w -> 1 - w` first. Level 0 = untouched, level L =
  largest blocks.

### 4. Blockify (coarsest first)

```
for L in (Lmax .. 1):
    for every aligned block of 2^L base cells:
        if block already covered by a coarser one: skip
        cold = min(level over the block) >= L          # whole block in the cold zone
        cnt  = number of occupied base cells in the block
        if cold and cnt > 0:
            solid = cnt >= Fill Threshold * 8^L        # fill 0 -> cnt > 0
            set every base cell in the block to `solid`
```

Two rules matter, both learned from the spike:

- **hot blocks are never touched** — a block that is not fully cold keeps its
  fine occupancy, otherwise the hot zone gets erased;
- **empty blocks are never made solid**, whatever the threshold, otherwise the
  whole bounding box becomes a brick.

`Fill Threshold` (0..1, default 0.5) decides between fattening and thinning:
0 = any occupied base cell makes the block solid (nothing is lost, the cold zone
grows by up to one block), 0.5 = majority replica of the original, 1 = only fully
occupied blocks are kept (thin cold features can disappear).

### 5. Re-run the diagonal-contact fix

The coarse lattice creates new checkerboard contacts that the pass running earlier
cannot have seen. The existing slice-shift pass is factored into a helper and
called once more after blockification. Measured in the spike: it converges
immediately (`recheck +0`), so the cost is one pass.

### 6. Everything downstream

Unchanged. Geometry is emitted per base cell, so the surface of a blockified
region is a valid boundary of a cell set: no gaps, no T-junctions, and the
existing welding / `fill_open_edges` / `separate` behaviour carries over.
Coarse areas simply end up as coplanar quads that do not add detail.

## Settings

All operator properties (dialog + `_SNA_VOXEL_PERSIST` for the JSON stash).

| Property | UI name | Type / default | Purpose |
|---|---|---|---|
| `size_map_enabled` | Size Map (Weight Paint) | bool, False | master switch |
| `size_map_group` | Vertex Group | string, '' | prop_search over `obj.vertex_groups`; string keeps it JSON-safe |
| `size_map_max` | Max Block Size | enum 2x / 4x / 8x, default 4x | Lmax = 1 / 2 / 3 |
| `size_map_curve` | Response | float 0.2..5, default 1.0 | gamma of weight -> level |
| `size_map_fill` | Fill Threshold | float 0..1, default 0.5 | block becomes solid at this occupied fraction |
| `size_map_smoothing` | Smoothing Passes | int 0..8, default 2 | box-filter passes over the weight field |
| `size_map_invert` | Invert (hot = bigger) | bool, False | for maps painted the other way |

Tooltips state: unpainted = coldest = biggest cube; 0 = nothing is ever lost but
the cold zone gets fatter; 1 = thinnest result but cold details can disappear;
and that the memory cost equals a uniform run at the smallest size (0.4 mm is the
practical print floor for a 0.4 mm nozzle).

UI: a labelled group after the tone block, `Size Map (Weight Paint):`; dependent
controls (`group`, `max`, `curve`, `fill`, `smoothing`, `invert`) are drawn only
when enabled, like the existing `collapse_dist` conditional. The dialog draws
must go into the live `draw()` (the earlier one is dead code shadowed by it).

Result name: the `{cell}mm` token becomes a range when the feature is on, e.g.
`MAT_1-4mm_K8_g1_gray_..._Voxel`.

Validation at execute(): group missing / empty (all weights 0) / constant map
(max == min) -> `report({'ERROR'})` and cancel, mirroring the existing checks for
UV map and base texture.

## Validation performed (spike, not shipped)

Real model (Meshy relief, 500k tris) at 1 mm cells, cold zone at 4x, hot disc in
the centre, face-material mode, no separation:

| variant | faces | boundary edges | non-manifold edges | components |
|---|---|---|---|---|
| uniform (today) | 2,749,524 | 0 | 0 | 1 |
| quantised, fill 0.5 | 151,834 | 0 | 0 | 1 |
| quantised, fill 0.0 | 153,222 | 0 | 0 | 4 |

- watertight and single-component in all variants — the fine-lattice emission is
  crack-free by construction;
- fill 0.0 disconnects material (isolated blocks appear) — hence the 0.5 default;
- render comparison: `F:/ebc_debug/real_compare.png` (uniform | fill 0.5 |
  fill 0.0).

Two spike bugs confirmed the two safety rules in section 4 (erasing hot blocks,
filling empty blocks), both now explicit in the design.

## Risks

- **Thin cold features** (1-2 base cells) are at the mercy of `Fill Threshold`:
  erasing them can disconnect a part. Mitigation: default 0.5, tooltip, and the
  existing post-run checks in the user's workflow; a "keep thin details" guard
  (erode-test before coarsening) is deliberately out of scope for v1 and can be
  added later if it bites.
- **Guard message** still speaks one size while the grid now runs at the smallest
  size — the message stays correct in cell terms (the grid is the finest size),
  but the tooltip must say it.
- **Palette drift**: k-means samples per emitted face, so a gradient shifts the
  sample distribution; deterministic seed 42 still applies, the palette just
  differs from a uniform run. Expected, not a defect.
- **`fill_open_edges` tail**: measured earlier at >8 min on a 1.6M-face run; with
  the gradient the face count drops hard, which should cut that tail.

## Test plan

- New F3 self-test `sna.test_size_map`: synthetic grid, asserts that (a) hot
  blocks keep their fine occupancy, (b) empty blocks are never filled, (c) the
  result has no boundary edges after weld, (d) `fill=0.5` vs `fill=0` differ
  exactly on partially occupied blocks.
- Headless harness (f:/ebc_debug pattern) on the real Meshy relief, A/B against
  the uniform run: face count, boundary/non-manifold edges, components, plus the
  side-by-side render — the run used for this spec is kept as the baseline.
- Manual: paint a weight group on a real model, run with 2x / 4x / 8x, check the
  outliner name and that the hot zone is untouched.
