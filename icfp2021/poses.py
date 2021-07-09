#!/usr/bin/env python3
'''
Wire format
Problems and poses are encoded in JSON. A complete example of a problem is given at the bottom of this
section.

Points Points are encoded as a JSON array holding the X and Y coordinate, in that order. Coordinates are
always integers.

Hole A hole is encoded as a JSON array containing all vertices of the hole in order. The minimum number
of vertices is 3.

Figure A figure is encoded as a JSON object with two properties:
• vertices: An array of points, indicating the initial locations of the vertices. The minimum
number of vertices is 2.
• edges: An array of pairs, where each pair represents a line segment between the two vertices. The
pairs are given as two 0-based indices into the vertices array. The pairs can be specified in either
order. The minimum number of edges is 1.

Problem A problem is encoded as a JSON object with the following properties:
• hole: A hole as defined above.
• figure: A figure as defined above.
• epsilon: The ε used for this problem.

Pose A pose is encoded as a JSON object with a single property:
• vertices: An array of points, indicating the new positions of points in the assumed pose.

As a full example, here is the JSON encoding of the “Lambdaman” problem.
{
"hole": [
[55, 80], [65, 95], [95, 95], [35, 5], [5, 5],
[35, 50], [5, 95], [35, 95], [45, 80]
],
"figure": {
"edges": [
[2, 5], [5, 4], [4, 1], [1, 0], [0, 8], [8, 3], [3, 7],
[7, 11], [11, 13], [13, 12], [12, 18], [18, 19], [19, 14],
[14, 15], [15, 17], [17, 16], [16, 10], [10, 6], [6, 2],
[8, 12], [7, 9], [9, 3], [8, 9], [9, 12], [13, 9], [9, 11],
[4, 8], [12, 14], [5, 10], [10, 15]
],
"vertices": [
[20, 30], [20, 40], [30, 95], [40, 15], [40, 35], [40, 65],
[40, 95], [45, 5], [45, 25], [50, 15], [50, 70], [55, 5],
[55, 25], [60, 15], [60, 35], [60, 65], [60, 95], [70, 95],
[80, 30], [80, 40]
]
},
"epsilon": 150000
}
And this is the JSON encoding of the pose in the figure we saw earlier:
{
"vertices": [
[21, 28], [31, 28], [31, 87], [29, 41], [44, 43], [58, 70],
[38, 79], [32, 31], [36, 50], [39, 40], [66, 77], [42, 29],
[46, 49], [49, 38], [39, 57], [69, 66], [41, 70], [39, 60],
[42, 25], [40, 35]
]
}
'''
