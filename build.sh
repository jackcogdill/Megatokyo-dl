#! /bin/bash

pushd "$(dirname $0)"
cd src

executable="megatokyo-dl"
zipfile="${executable}.zip"
temp="temp"

# Create new pyc files
rm -f *.pyc
python -m compileall .
zip "$zipfile" __main__.py *
cd ..

rm -f "$executable"
mv "src/$zipfile" "$temp"

echo "#! /usr/bin/env python" > "$executable"
cat "$temp" >> "$executable"
rm "$temp"

chmod +x "$executable"

popd

