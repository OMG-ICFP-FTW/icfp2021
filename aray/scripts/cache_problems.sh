#!/bin/bash


for i in $(seq 1 132); do curl -i -H "Authorization: Bearer $ICFP2021_API_KEY" https://poses.live/api/problems/$i > /tmp/$i.problem;  done