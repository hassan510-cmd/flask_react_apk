#https://yingshaoxo.blogspot.com/2020/03/how-to-use-docker-to-build-kivy-to.html

export ANDROIDSDK="/home/sedosona/.buildozer/android/platform/android-sdk"
export ANDROIDNDK="/home/sedosona/.buildozer/android/platform/android-ndk-r19c"
export ANDROIDAPI="27"  # Target API version of your application
export NDKAPI="21"  # Minimum supported API version of your application
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"

#p4a clean_builds
#p4a clean_dists
p4a apk --private . \
    --package=org.pay.buy \
    --name "Pay Buy" \
    --version 0.1 \
    --bootstrap=webview \
    --requirements=python3,flask,flask_cors,itsdangerous==2.0.0,flask_sqlalchemy,sqlalchemy,flask_marshmallow,marshmallow \
    --permission INTERNET --permission WRITE_EXTERNAL_STORAGE \
    --port=8888 --icon ./logo.png \
