#!/bin/bash

D=$(pushd $(dirname $0) &> /dev/null; pwd; popd &> /dev/null)
P=${D}/ipkg.tmp.$$
B=${D}/ipkg.build.$$

pushd ${D} &> /dev/null
#GITVER=git$(git log -1 --format="%ci" | awk -F" " '{ print $1 }' | tr -d "-")
GITVER="1.1-rc3"
PKG=${D}/enigma2-plugin-extensions-baseplugin_${GITVER}_all.ipk
popd &> /dev/null

mkdir -p ${P}
mkdir -p ${P}/CONTROL
mkdir -p ${B}

cat > ${P}/CONTROL/control << EOF
Package: enigma2-plugin-extensions-baseplugin
Version: ${GITVER}
Section: cams
Priority: optional
Architecture: all
Maintainer: www.linux-box.es
Depends: 
Description: Linux-Box Base Panel control for enigma2
Source: n/a
Homepage: http://www.linux-box.es
EOF

cp -rp ${D}/baseplugin/* ${P}/

tar -C ${P} -czf ${B}/data.tar.gz . --exclude=CONTROL
tar -C ${P}/CONTROL -czf ${B}/control.tar.gz .

echo "2.0" > ${B}/debian-binary

cd ${B}
ls -la
ar -r ${PKG} ./debian-binary ./data.tar.gz ./control.tar.gz 
cd -

rm -rf ${P}
rm -rf ${B}
