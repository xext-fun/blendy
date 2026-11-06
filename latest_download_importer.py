"""Import the newest supported 3D file from Downloads into the current scene."""

bl_info = {
    "name": "Latest Download Importer",
    "author": "xext-fun",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Downloads",
    "description": "Import the newest supported model in your Downloads folder",
    "category": "Import-Export",
}

from pathlib import Path

import bpy
from bpy.props import StringProperty


# The first available registered operator for each format is used. Optional
# Blender import add-ons can provide some of the operators in this table.
IMPORTERS = {
    ".obj": ("wm.obj_import", "import_scene.obj"),
    ".fbx": ("wm.fbx_import", "import_scene.fbx"),
    ".glb": ("import_scene.gltf",),
    ".gltf": ("import_scene.gltf",),
    ".stl": ("wm.stl_import", "import_mesh.stl"),
    ".ply": ("wm.ply_import", "import_mesh.ply"),
    ".abc": ("wm.alembic_import",),
    ".usd": ("wm.usd_import",),
    ".usda": ("wm.usd_import",),
    ".usdc": ("wm.usd_import",),
    ".usdz": ("wm.usd_import",),
    ".dae": ("wm.collada_import",),
    ".bvh": ("import_anim.bvh",),
    ".3ds": ("import_scene.max3ds",),
    ".x3d": ("import_scene.x3d",),
    ".wrl": ("import_scene.x3d",),
    ".dxf": ("import_scene.dxf",),
    ".blend": (),
}

INCOMPLETE_SUFFIXES = {".crdownload", ".part", ".partial", ".download", ".tmp"}


def _operator(idname):
    category, name = idname.split(".", 1)
    try:
        operator = getattr(getattr(bpy.ops, category), name)
        operator.get_rna_type()
    except (AttributeError, KeyError, RuntimeError):
        return None
    return operator


def available_importer(suffix):
    if suffix == ".blend":
        return "blend"
    for idname in IMPORTERS.get(suffix, ()):
        if _operator(idname) is not None:
            return idname
    return None


def newest_model(folder, excluded_path=None):
    """Return (path, importer), or (None, None) if none is usable."""
    candidates = []
    for path in folder.iterdir():
        if excluded_path and path.resolve() == excluded_path.resolve():
            continue
        if not path.is_file() or path.suffix.lower() in INCOMPLETE_SUFFIXES:
            continue
        importer = available_importer(path.suffix.lower())
        if importer is None:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_size > 0:
            candidates.append((stat.st_mtime_ns, path.name, path, importer))
    if not candidates:
        return None, None
    _, _, path, importer = max(candidates)
    return path, importer


def append_blend_objects(filepath, collection):
    """Append all objects without replacing the open Blender project."""
    with bpy.data.libraries.load(str(filepath), link=False) as (source, target):
        target.objects = source.objects
    count = 0
    for obj in target.objects:
        if obj is not None:
            collection.objects.link(obj)
            count += 1
    return count


class LDI_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    downloads_folder: StringProperty(
        name="Downloads folder",
        subtype="DIR_PATH",
        default="~/Downloads",
        description="Folder checked when the import button is clicked",
    )

    def draw(self, context):
        self.layout.prop(self, "downloads_folder")


class LDI_OT_import_latest(bpy.types.Operator):
    bl_idname = "ldi.import_latest"
    bl_label = "Import Latest Download"
    bl_description = "Import the newest supported 3D file in the configured folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preferences = context.preferences.addons[__name__].preferences
        folder = Path(bpy.path.abspath(preferences.downloads_folder)).expanduser()
        if not folder.is_dir():
            self.report({"ERROR"}, f"Downloads folder does not exist: {folder}")
            return {"CANCELLED"}

        try:
            current_file = Path(bpy.data.filepath) if bpy.data.filepath else None
            path, importer = newest_model(folder, current_file)
        except OSError as exc:
            self.report({"ERROR"}, f"Cannot read Downloads folder: {exc}")
            return {"CANCELLED"}
        if path is None:
            self.report({"WARNING"}, "No supported, nonempty 3D file found")
            return {"CANCELLED"}

        try:
            if importer == "blend":
                count = append_blend_objects(path, context.collection)
                if count == 0:
                    self.report({"WARNING"}, f"No objects found in {path.name}")
                    return {"CANCELLED"}
            else:
                result = _operator(importer)(filepath=str(path))
                if "FINISHED" not in result:
                    self.report({"ERROR"}, f"Import cancelled: {path.name}")
                    return {"CANCELLED"}
        except Exception as exc:
            self.report({"ERROR"}, f"Could not import {path.name}: {exc}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Imported {path.name}")
        return {"FINISHED"}


class LDI_PT_downloads(bpy.types.Panel):
    bl_label = "Latest Download"
    bl_idname = "LDI_PT_downloads"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Downloads"

    def draw(self, context):
        self.layout.operator(LDI_OT_import_latest.bl_idname, icon="IMPORT")


CLASSES = (LDI_AddonPreferences, LDI_OT_import_latest, LDI_PT_downloads)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
