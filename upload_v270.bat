set VERSION=2.7.0
set CDN_URL=http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com/
python wheel-uploader.py -r pypi -u %CDN_URL% -v -w ./wheelhouse -t macosx numexpr %VERSION%
python wheel-uploader.py -r pypi -u %CDN_URL% -v -w ./wheelhouse -t manylinux1 numexpr %VERSION%
python wheel-uploader.py -r pypi -u %CDN_URL% -v -w ./wheelhouse -t win numexpr %VERSION%