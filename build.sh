#!/bin/bash

# get current time
BUILD_TIME=$(date -u +"%Y-%m-%d %H:%M:%S")

# update Python build time
sed -i '' "s/self.build_time = \".*\"/self.build_time = \"$BUILD_TIME\"/" myRocksDbViewer.py

#  PyInstaller packing
pyinstaller build.spec --clean --noconfirm

# create DMG
create-dmg \
  --volname "RocksDB Viewer" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "RocksDBViewer.dmg" \
  "dist/RocksDBViewer.app"

echo "Build completed at $BUILD_TIME"
