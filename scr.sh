#!/bin/bash
# 1 timestamp
# 2 timestamp
# 3 file
# 4 logo file
# 5 logo file
# 6 team color (not implemented)
# 7 team color (not implemented)
# 8 team
# 9 team
# 10 score
# 11 score
# 12 output file
ffmpeg -ss $1 -to $2 -i $3 -i $4 -i $5 -filter_complex \
	"[0]drawbox=x=(3*iw)/80:y=(3*iw)/80:w=iw/10:h=iw/20:c=Black:t=fill, \
	    drawbox=x=(3*iw)/80+iw/10:y=(3*iw)/80:w=iw/40:h=iw/20:c=White:t=fill, \
	    drawtext=text=$8:x=(3*W)/80+W/240+W/40:y=(3*W)/80+W/80-th/2:fontsize=W/80:fontcolor=White:fontfile=bin/DejaVuSans-Bold.ttf, \
	    drawtext=text=$9:x=(3*W)/80+W/240+W/40:y=(3*W)/80+W/40+W/80-th/2:fontsize=W/80:fontcolor=White:fontfile=bin/DejaVuSans-Bold.ttf, \
	    drawtext=text=${10}:x=((3*W)/80+W/10)+(W/40-tw)/2:y=(3*W)/80+W/80-th/2:fontsize=W/80:fontcolor=Red:fontfile=bin/DejaVuSans-Bold.ttf, \
	    drawtext=text=${11}:x=((3*W)/80+W/10)+(W/40-tw)/2:y=(3*W)/80+W/40+W/80-th/2:fontsize=W/80:fontcolor=Red:fontfile=bin/DejaVuSans-Bold.ttf[0_text]; \
	 [1][0_text]scale2ref=w=iw/60:h=iw/60[ol1][0_text1]; \
	 [2][0_text1]scale2ref=w=iw/60:h=iw/60[ol2][0_text2]; \
	 [0_text2][ol1]overlay=x=(3*W)/80+W/240:y=(3*W)/80+W/240[0_text2_o1]; \
	 [0_text2_o1][ol2]overlay=x=(3*W)/80+W/240:y=(3*W)/80+W/240+W/40" \
	 -c:a copy ${12}

# Test call:
# ./scr.sh 00:00:03 00:00:04 test/vsMaine/C0001.MP4 test/vsMaine/train.gif test/vsMaine/maine.jpg Black White TRAIN MAINE 10 1 out/test.mov
