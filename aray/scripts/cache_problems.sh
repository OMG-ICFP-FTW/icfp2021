#!/bin/bash


for i in $(seq 1 132); do curl -H "Authorization: Bearer $ICFP2021_API_KEY" https://poses.live/api/problems/$i > /tmp/$i.problem & done

# for i in $(seq 1 132); do ./forbidden $i /tmp/$i.problem & done