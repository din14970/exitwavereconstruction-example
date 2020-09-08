#!/bin/bash
DIREC="$*"
echo "Converting SER files in $DIREC"
for i in "${DIREC}"*.ser
do
    echo "Found $i"
    [ -f "$i" ] || continue
    convertSERToQuoc "${i}"
    filename=$(basename -- "$i")
    filename="${filename%.*}"
    quocname="${filename}000.q2bz"
    newname="${filename}.q2bz"
    echo "Moving $quocname to $DIREC$newname"
    [ -f "$quocname" ] || continue
    mv "$quocname" "${DIREC}${newname}" 
    rm "$i"
    echo "Removed $i"
    echo "------------------"
done

    
