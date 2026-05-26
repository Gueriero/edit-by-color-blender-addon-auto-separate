# Edit by Color by KIRI Engine
<a href="./LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>

## Introduction:
The Colour Selection panel provides intuitive controls to precisely select mesh elements based on their texture colors, with adjustable tolerance and selection refinement options.

Live Effects, powered by Geometry Nodes, enables real-time deletion, smoothing, and material assignment while dynamically adjusting your color selection.

The Edit Mesh panel hosts essential editing operations that let you duplicate selected areas to new objects, split them from the current mesh, or simply convert them into Edit Mode selections.

For Sculpt mode, convert your colour selections into Face Sets for targeted sculpting and smoothing operations, making high-density scan editing more manageable, especially for beginners.

The Texture baking system allows you to create, replace, and rebake selected areas of your model's texture, perfect for removing unwanted details or surface imperfections.

Retopo Loops automatically generate clean quad topology around colour-selected areas to jump start your retopology workflow on scanned models.

## Installation:
❗❗Please note❗❗ The addon was made for the most current version of Blender at the time of writing. The addon should be capable of 4.2 and later, and will NOT work with previous versions of Blender. 

Please follow the installation guide in the [doc](https://www.kiriengine.app/blender-addon/edit-by-colour).

## Tutorial:
The instructions can be found in [doc](https://www.kiriengine.app/blender-addon/edit-by-colour).
The tutorial video can be found [here](https://www.youtube.com/watch?v=RRAivqua1rc).
More "Fun" tutorial video can be found [here](https://youtu.be/1-XXchwXNE8).

## Fork additions — Palette Split (3D Print)

This fork adds a new section at the bottom of the **Edit By Colour** panel:
**Palette Split (3D Print)**. It quantizes a textured mesh into a manual
color palette with per-color gradient steps, assigns flat materials per
bucket, and separates the result into individual mesh objects — ready for
multi-color 3D printing on printers with limited filament slots.

### How it works
1. Per-face barycentric sampling of the base texture (multiple samples
   averaged inside each UV triangle for accuracy).
2. Each face is matched to the nearest palette color using **HSV distance**
   (desaturated samples are biased toward desaturated palette entries so
   blue does not drift into grey).
3. Within that base color, the face is binned by relative luminance
   (`0.2126·R + 0.7152·G + 0.0722·B`) into N tonal steps (configurable
   per palette entry).
4. A flat material `EBC_Pal_{base}_{bin}` is created for each bucket with
   `Base Color = base × tone_multiplier` (multiplier range 0.3..1.0 so the
   darkest bin keeps its hue instead of going black).
5. Optionally runs `mesh.separate(type='MATERIAL')` to produce one mesh
   per bucket.

The UV Map and Base Texture are read from the existing
`KIRI_Edit_By_Colour_GN` modifier (Socket_2 / Socket_4) — no extra fields
to configure.

### Usage
1. **Object Mode**, with a textured mesh active.
2. Click **Add Edit By Colour Modifier**, then set **UV Map** and **Base
   Texture** in the Active Object box (as you would for normal Edit By
   Colour use).
3. Scroll the panel down to **Palette Split (3D Print)**.
4. Click **+** to add a palette entry. Click the color swatch to open the
   Blender color picker — use its built-in **eyedropper** to sample a base
   color from the texture in the viewport / Image Editor. Set **Steps**
   (number of tonal bins for this base color, 1–16).
5. Repeat for every base color in your palette (e.g. white, black, grey,
   blue → 4 entries).
6. Click **Split & Colorize**. In the dialog:
   - **Samples per Face** — how many barycentric samples to average per
     face (default 7; raise for accuracy on small faces, lower for speed
     on large meshes).
   - **Separate by Material** — if enabled, splits the mesh into one
     object per color bucket.
7. The Outliner will contain N objects, one per bucket, each with its own
   flat material. Each object is ready to be exported and printed in the
   corresponding filament color.

### Notes
- If UV Map or Base Texture is missing on the modifier, the operator will
  refuse to run and tell you which.
- Reading large textures can take a few seconds (pixels are read in one
  pass at the start).
- The tone multiplier is `0.3..1.0` by design — the darkest bin of any
  color keeps its hue so different "darks" don't all become identical
  black. If you actually want a pure-black darkest bin, edit the
  `v_mul` line in `__init__.py`.

## Fork additions — Auto Palette Split (k-means)

A second new section below **Palette Split**: **Auto Palette Split
(k-means)**. Instead of picking colors manually, you specify a target
number of buckets (e.g. 16, 64, 128) and the operator finds dominant
colors in the texture automatically and assigns each face to its nearest
cluster.

### How it works
1. Reads the same UV Map / Base Texture as the manual mode (from the
   `KIRI_Edit_By_Colour_GN` modifier).
2. Samples an average RGB color per face (barycentric points inside each
   UV triangle).
3. Runs **k-means++** clustering (`K` = requested number of colors) on a
   random subsample of faces for speed. Iterates Lloyd's algorithm until
   centroids stabilise.
4. By default clusters in **HSV space** (hue mapped to circular x/y to
   keep euclidean k-means valid) so red ↔ red is closer than red ↔ blue
   regardless of luminance. RGB mode is available as a toggle.
5. Assigns every face to its nearest cluster, creates one flat material
   per cluster (`EBC_Auto_NNN`) with `Base Color` = cluster centroid, and
   optionally separates by material.

### Usage
1. Object Mode with active textured mesh and Edit By Colour modifier set
   up (UV Map + Base Texture).
2. Bottom of the panel → **Auto Palette Split (k-means)** →
   **Auto Detect & Split**.
3. In the dialog:
   - **Total Colors** — number of buckets to produce (2..256).
   - **Samples per Face** — barycentric sample density (default 4).
   - **Cluster in HSV** — recommended on; off uses raw RGB euclidean.
   - **Separate by Material** — produce one mesh per cluster.
   - Advanced: **K-means Iterations**, **Cluster Sample Cap** (random
     subsample of faces used to fit centroids — speeds up huge meshes).
4. Result: N material slots + N separated meshes (some clusters may be
   empty if the requested K is higher than the actual color variety in
   the texture — those are skipped).

### Manual vs Auto — which to use
- **Manual Palette Split** — when you know the exact filament colors your
  printer has and want full control over base hues and tonal steps per
  hue.
- **Auto Palette Split** — when you want the addon to discover the
  palette from the texture itself, or when you need many buckets (64,
  128…) that would be tedious to define manually.

Both blocks are independent. You can run either or both.

## Acknowledgement:
Thanks to everybody who contributes to this good work from the KIRI Engine team.

This fork by [Gueriero](https://github.com/Gueriero) extends the addon
with the Palette Split feature described above. All credit for the
original Edit By Colour addon goes to the KIRI Engine team.
