#!/bin/bash -e

AWS_STORAGE_BUCKET_NAME=luna-mobile-dev

export AWS_SECRET_ACCESS_KEY=
export AWS_ACCESS_KEY_ID=

CDN_PATH=/mnt/CDN1/p/

for avatar_file in `find $CDN_PATH -type f -name *MASTER.jpg`
do
	a=`dirname $avatar_file`
	d4=`dirname $a`
	d3=`dirname $d4`
	d2=`dirname $d3`
	d1=`dirname $d2`

	d4=`basename $d4`
	d3=`basename $d3`
	d2=`basename $d2`
	d1=`basename $d1`

	hid=$d1$d2$d3$d4

	echo "Uploading avatar $avatar_file for user $hid"

	aws s3 cp $avatar_file s3://$AWS_STORAGE_BUCKET_NAME/avatar/$hid.jpg
done
