#https://yingshaoxo.blogspot.com/2020/03/how-to-use-docker-to-build-kivy-to.html

export ANDROIDSDK="/home/code-flex-pc2/.buildozer/android/platform/android-sdk"
export ANDROIDNDK="/home/code-flex-pc2/.buildozer/android/platform/android-ndk-r19c"
export ANDROIDAPI="27"  # Target API version of your application
export NDKAPI="21"  # Minimum supported API version of your application

p4a clean_builds
p4a clean_dists
p4a clean_bootstrap_builds
p4a apk --private . \
	--package=or.ts \
	--name "ver001" \
	--version 0.1 \
	--bootstrap=webview \
	--requirements=python3,flask,flask_cors,itsdangerous==2.0.0 \
	--permission INTERNET --permission WRITE_EXTERNAL_STORAGE \
	--port=8888 \
	--presplash "./wallet.png" \
	--icon "./icon.png" \
	--android-entrypoint main.pyc 

