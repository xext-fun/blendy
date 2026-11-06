# Latest Download Importer for Blender

Import the newest supported 3D model in your Downloads folder with one click. The add-on checks the folder each time you click, so you can download an updated model and preview it in your current Blender scene immediately.

## Install

1. Download [`latest_download_importer.py`](latest_download_importer.py) from this repository. Keep it as a `.py` file.
2. In Blender, open **Edit > Preferences > Add-ons**. Click the menu in the upper right, then **Install from Disk…** (in some Blender versions, **Install…**).
3. Select `latest_download_importer.py`, install it, and enable **Latest Download Importer** if Blender does not enable it automatically.
4. In the 3D Viewport, press **N** to show the sidebar. Open the **Downloads** tab and click **Import Latest Download**.

The default folder is `~/Downloads`. To change it, open the add-on's entry in **Preferences > Add-ons** and set **Downloads folder**.

## Supported files

The add-on recognizes `.blend`, `.obj`, `.fbx`, `.glb`, `.gltf`, `.stl`, `.ply`, `.abc`, `.usd`, `.usda`, `.usdc`, `.usdz`, `.dae`, `.bvh`, `.3ds`, `.x3d`, `.wrl`, and `.dxf`. It uses Blender's installed import operator for each format. Some formats require their corresponding Blender import add-on to be enabled. An unsupported or unavailable format is skipped while finding the latest usable file.

The newest file is determined by its modification time. Empty files, folders, partial downloads such as `.crdownload` and `.part`, and the currently open `.blend` file are ignored. `.blend` files contribute their objects to the current scene; they do not replace your open project. Other imports also add to the current scene, so clicking twice imports a second copy. The add-on does not unpack ZIP archives.

For `.gltf` and similar formats with external textures or buffers, keep those companion files beside the model in Downloads.

## Development

The add-on targets Blender 4.0 or newer and has no Python dependencies beyond Blender itself. Install the source file directly for local development.
