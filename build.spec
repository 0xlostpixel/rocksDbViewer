# build.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['myRocksDbViewer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RocksDBViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    codesign_identity=None,
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='RocksDBViewer.app',
    icon='./rdv.icns',
    bundle_identifier='com.rocksdb.viewer',
    info_plist={
        'CFBundleName': 'RocksDB Viewer',
        'CFBundleDisplayName': 'RocksDB Viewer',
        'CFBundleGetInfoString': "RocksDB Viewer",
        'CFBundleIdentifier': "com.rocksdb.viewer",
        'CFBundleVersion': "1.0.5",
        'CFBundleShortVersionString': "1.0.5",
        'NSHighResolutionCapable': 'True',
    },
)
