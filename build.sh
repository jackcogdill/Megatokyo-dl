#! /bin/bash

pushd "$(dirname $0)"
cd src

executable="megatokyo-dl"
zipfile="${executable}.zip"

zip "$zipfile" __main__.py *.py
cd ..

rm -f "$executable"
mv "src/$zipfile" "$executable"

#command="cat $executable"
#echo -e "#! /usr/bin/env python\n$($command)" > "$executable"

chmod +x "$executable"

popd

