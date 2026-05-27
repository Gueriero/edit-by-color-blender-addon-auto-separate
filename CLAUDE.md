# Edit by Color by KIRI Engine — Fork с Palette Split

Форк официального Blender-аддона KIRI Engine. Добавляет нижние блоки **Palette Split** и **Auto Palette Split** для разбиения текстурированного меша на отдельные меши по цветам — для multicolor 3D-печати на принтерах с ограниченным числом филаментов.

## Репо

- **Origin (fork, push сюда):** https://github.com/Gueriero/edit-by-color-blender-addon-auto-separate
- **Upstream:** https://github.com/Kiri-Innovation/edit-by-color-blender-addon
- **Git identity** (локально в репо): `Gueriero` / `alexander.novgorodcev@gmail.com`. Глобально НЕ ставится.

## Лицензия

В репо конфликт: `LICENSE` = Apache 2.0, `blender_manifest.toml` = GPL-2.0-or-later. Реально применимо GPL (Blender-аддоны линкуются с bpy). При публикации форка **сохраняй оба файла** + атрибуцию KIRI.

## Среда пользователя

- **OS:** Windows 10, PowerShell 5.1
- **Blender:** 5.0.1 (на 4.x тоже должно работать, manifest min=4.2.0)
- **Scene units:** Metric, Length display = Millimeters. 1 BU = 1 m, отображается в mm. FloatProperty с `unit='LENGTH'` сам конвертит.
- **C:\ диск забит (0 GB free)** — staging temp в `%TEMP%` падает. Использовать F: или писать zip напрямую через .NET API (см. ниже).
- **Целевой меш:** ~1.5M полигонов, текстура 4096×4096.

## Сборка zip (без staging)

`Compress-Archive` требует staging-папку для корневого имени внутри архива. Из-за C:\ обходим через `System.IO.Compression.ZipFile`:

```powershell
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$src='F:\Edit by Color by KIRI Engine'
$zip = Join-Path $src ("edit_by_color_by_kiri_engine_v{0}.zip" -f '2.9.0')
if(Test-Path -LiteralPath $zip){ Remove-Item -LiteralPath $zip -Force }
$arch = [System.IO.Compression.ZipFile]::Open($zip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
  Get-ChildItem -LiteralPath $src -Recurse -File -Force | Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and $_.Extension -ne '.zip' -and $_.Name -ne '.gitignore'
  } | ForEach-Object {
    $rel = $_.FullName.Substring($src.Length + 1) -replace '\\','/'
    $entry = 'edit_by_color_by_kiri_engine/' + $rel
    [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
      $arch, $_.FullName, $entry, [System.IO.Compression.CompressionLevel]::Optimal)
  }
} finally { $arch.Dispose() }
```

`Compress-Archive`, `Remove-Item -Recurse` на корне F: блокируются sandbox-защитой.

## Workflow выпуска версии

1. Edit code in [__init__.py](__init__.py).
2. Bump `version = "X.Y.Z"` в [blender_manifest.toml](blender_manifest.toml).
3. `git add ... && git commit -m "..."` + `git push`.
4. Собрать zip скриптом выше (имя: `edit_by_color_by_kiri_engine_vX.Y.Z.zip`).
5. Старые zip'ы в `.gitignore`, в репо не пушатся.

Если нужно восстановить старый zip — `git checkout <hash>` → собрать zip → `git checkout main` → `git stash pop` (если были uncommitted).

## Архитектура аддона

### Palette Split (manual)
Ручная палитра + пипетка цвета + steps на базовый цвет. Per-face барицентрический сэмплинг текстуры → ближайший базовый цвет по HSV → бин по luminance → flat material → `mesh.separate`.

### Auto Palette Split (k-means) — модальный оператор
Класс `SNA_OT_auto_palette_split`. **Модальный оператор с генератором** — `_work(...)` yield-ит `(text, pct)`, `modal()` тикает таймером 0.08s, обновляет `context.workspace.status_text_set` со спиннером + ESC отменяет. Это единственный способ показать live UI во время блокирующего Python.

Pipeline (фазы):
1. Read image pixels (numpy `foreach_get`)
2. Sample per-face avg color (барицентрика по UV)
3. HSV transform (hue → cos/sin для евклидова k-means)
4. K-means++ init + Lloyd на подвыборке
5. Assign all faces (chunked, OOM-safe)
6. **Optional: Merge Small Islands** (см. ниже)
7. Create materials per cluster
8. Write `material_index` через `foreach_set` + numpy lookup table
9. Remove KIRI modifier (опционально)
10. Separate — атомарный `mesh.separate(MATERIAL)` или Progressive (per-cluster логи)

### Merge Small Islands — фильтры

Connected components внутри одного cluster label через union-find. Затем фильтрация мелких + reassign в majority neighbor cluster.

Фильтры (любой триггерит merge):
- **AABB min X / Y / Z** — мировые оси, 0 = ось не проверяется
- **Min Feature Width (OBB)** — наименьший principal axis из PCA. Ловит диагональные тонкие фичи которые AABB упускает
- **Min Island Faces** — минимум полигонов
- **Erosion Passes** — морфологическая эрозия per-face (N проходов): грань с минoritarian same-cluster соседями переключается в majority. Работает независимо от bbox/топологии. Единственное что справляется с тонкими ВЕНАМИ внутри топологически связных компонентов

## Критические Blender 5.0.1 баги

**`polygon.select` через `foreach_set` в Object mode НЕ синхронизируется в bmesh.** Если выставить selection через `data.polygons.foreach_set('select', sel)` и потом перейти в Edit + `mesh.separate(SELECTED)` — bmesh видит ВСЕ грани как selected, весь меш улетает в новый объект.

**Workaround:** использовать `bpy.ops.object.material_slot_select` для выделения граней слота. Стандартный C-оператор, идёт через bmesh правильно.

Применено в Progressive Separate (Auto Palette Split). Цикл остаётся в Edit mode на всех итерациях → один mode switch.

## Тест-операторы (F3, не в UI)

- `sna.test_progressive_separate` — synthetic plane + 4 материала, проверка mesh.separate механизма.
- `sna.test_merge_islands` — 200мм plane 20×20, 1-cell + 3×3 острова, проверка merge logic.

Из UI убраны после фиксов, доступны через F3 search.

## Стиль ответов

- **Caveman mode**: терсно, без филлера. Артикли/«really»/«basically» опускать. Технические термины точные, ошибки в кавычках.
- Язык переписки: **русский**.
- Commit messages: английский, conventional style.
- Code comments: минимум, только non-obvious WHY.
