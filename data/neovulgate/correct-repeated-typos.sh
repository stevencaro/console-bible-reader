#!/bin/bash
cmd=$(basename $0 .sh)

if [ $# -ne 2 ] ; then
        echo $cmd: usage is: $cmd \"\<bad string\>\" \"\<good string\>\"
        exit 1
fi

bad="$1"
good="$2"

for file in `grep -l "$bad" *.xml` ; do
        echo $file: changing \"$bad\" into \"$good\"...
        sed -i "/$bad/s//$good/" $file
done

red=$(tput setaf 1)
reset=$(tput sgr0)

if [ -z "$file" ] ; then     
        echo $cmd: ${red}no match${reset}
fi
