[app]

# (str) Title of your application
title = TORQ

# (str) Package name
package.name = torq

# (str) Package domain
package.domain = com.torq

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,pyjnius,android

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (int) Android SDK version
android.sdk = 33

# (bool) Use --private data storage
android.private_storage = True

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for
android.archs = arm64-v8a,armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) The format used to package the app for release mode
android.release_artifact = apk

# (bool) Skip byte compile for .py files
android.no-byte-compile-python = False

# (str) Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Android addons
android.add_src = 

# (list) Android gradle dependencies
android.gradle_dependencies = 

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) python-for-android branch to use
#p4a.branch = master

# (str) python-for-android git clone directory
#p4a.source_dir = 

# (str) The directory in which python-for-android should look for your own build recipes
#p4a.local_recipes = 

# (str) Filename to the hook for p4a
#p4a.hook = 

# (str) Bootstrap to use for android builds
#p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifact storage
# build_dir = ./.buildozer

# (str) Path to build output storage
# bin_dir = ./bin