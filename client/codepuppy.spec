# -*- mode: python -*-
'''
pyinstaller script to package the codepuppy

usage: pyinstaller codepuppy.spec
'''
import os
import sys
import platform
#--------------------------------------------------------------------------------------------
# 1st step: get path set
path_set = []
path_set.append(os.path.abspath(os.curdir))

# --------------------------------------------------------------------------------------------
# 2nd step: get module set
def get_file_list(path, prefix=None):
    import os
    path_set = []
    for root,dirs,files in os.walk(path):
        for filename in files:
            if filename.startswith('_'):
                continue
            if filename.endswith('.py'):
                path_set.append(os.path.join(root, filename))
        for dirname in dirs:
            if dirname.startswith('_'):
                continue
            if root.find('.'):
                continue
            path_set.append(os.path.join(root, dirname))
    module_set = []
    for file_path in path_set:
        file_path = os.path.relpath(file_path, path)
        file_path = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        if prefix:
            prefix = prefix.replace('\\', '.').replace('/', '.')
            file_path = '%s.%s' % (prefix, file_path)
        module_set.append(file_path)
    return module_set


def get_cpython_suffix():
    if sys.platform.startswith("linux"):
        if platform.machine() == "aarch64":
            return "-aarch64-linux-gnu.so"
        else:
            return "-x86_64-linux-gnu.so"
    elif sys.platform.startswith(("win32", "cygwin")):
        return ".pyd"
    elif sys.platform.startswith("darwin"):
        return "-darwin.so"
    else:
        return ".so"

def get_cpython_file_list(root_dir, suffix=None):
    root_dir = os.path.abspath(root_dir)
    if type(suffix) == str:
        suffix = [suffix]
    binary_set = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(tuple(suffix)):
                path = os.path.join(root, filename)
                rel_dirpath = os.path.relpath(os.path.dirname(path), start=root_dir)
                prefix = rel_dirpath.replace('\\', '.').replace('/', '.')
                binary_set.append("%s.%s" % (prefix, filename.split('.')[0]))
    return binary_set


block_cipher = None
self_tool_module = get_file_list('tool','tool')
self_setting_module = get_file_list('settings','settings')
self_util_module = get_file_list('util', 'util')
self_task_module = get_file_list('task', 'task')
self_node_module = get_file_list('node', 'node')
third_party_module = ['psutil', 'yaml', 'html5lib', 'pyaes', 'pymongo', 'openpyxl', 'rsa', 'tqdm']
cpython_files = get_cpython_file_list('.', suffix=get_cpython_suffix())

total_set = []
total_set.extend(self_tool_module)
total_set.extend(self_setting_module)
total_set.extend(self_util_module)
total_set.extend(self_task_module)
total_set.extend(self_node_module)
total_set.extend(third_party_module)
total_set.extend(cpython_files)
# ------------------------------------------------------------------------------------------------
# 3th step: pack task.puppytask bin
a = Analysis(['task/puppytask.py'],
             pathex=path_set,
             binaries=[],
             datas=[],
             hiddenimports=total_set,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='scantask',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
# ------------------------------------------------------------------------------------------------
# 4th step: pack codepuppy bin
a = Analysis(['codepuppy.py'],
             pathex=path_set,
             binaries=[],
             datas=[],
             hiddenimports=total_set,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='codepuppy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
