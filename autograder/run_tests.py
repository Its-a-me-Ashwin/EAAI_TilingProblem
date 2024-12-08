import os
import json
import numpy as np
os.chdir('submission/')


###############################################################################

lines = open('hw1.py').readlines()
i=0
while True:
	if 'setup' in lines[i]:
		break
	i+=1
line_i_temp = lines[i].split('GUI')
lines[i] = ''.join([line_i_temp[0],"GUI = False, render_delay_sec = 0.0, gs = 9, num_colored_boxes=8)\n"])

f=open('hw1_test_1.py', 'w')
f.write(''.join(lines))
f.close()

os.system('python3 hw1_test_1.py')

data={}

time = float(open('time.txt', 'r').readlines()[0].rstrip())
shape_lines = open('shapes.txt', 'r').readlines()[0]
shape_lines = shape_lines.rstrip(')]').lstrip('[(').split('), (')
shape_list = []

for shape in shape_lines:
	sl = []
	shape_info = shape.split(', ')
	sl += [int(shape_info[0]), ]
	sl += [[int(shape_info[1].lstrip('[')), int(shape_info[2].rstrip(']'))], ]
	sl += [int(shape_info[3]), ]
	shape_list += [sl, ]

shapes_used = len(shape_list)

grid = np.loadtxt('grid.txt', dtype=int)
colors_used = len(np.unique(grid[grid!=-1]))
unfilled_cells = np.sum(grid==-1)

###############################################################################

lines[i] = ''.join([line_i_temp[0],"GUI = False, render_delay_sec = 0.0, gs = 11, num_colored_boxes=15)\n"])
f=open('hw1_test_2.py', 'w')
f.write(''.join(lines))
f.close()

os.system('python3 hw1_test_2.py')

time += float(open('time.txt', 'r').readlines()[0].rstrip())
shape_lines = open('shapes.txt', 'r').readlines()[0]
shape_lines = shape_lines.rstrip(')]').lstrip('[(').split('), (')
shape_list = []

for shape in shape_lines:
	sl = []
	shape_info = shape.split(', ')
	sl += [int(shape_info[0]), ]
	sl += [[int(shape_info[1].lstrip('[')), int(shape_info[2].rstrip(']'))], ]
	sl += [int(shape_info[3]), ]
	shape_list += [sl, ]

shapes_used = 0.5*shapes_used + 0.5*len(shape_list)

grid = np.loadtxt('grid.txt', dtype=int)
colors_used = 0.5*colors_used + 0.5*len(np.unique(grid[grid!=-1]))
unfilled_cells = 0.5*unfilled_cells + 0.5*np.sum(grid==-1)


###############################################################################

if colors_used<2:
	data['score']=0
if colors_used==2 and unfilled_cells==0:
	data['score'] = 35
elif colors_used<=3 and unfilled_cells==0:
	data['score'] = 30
else:
	data['score'] = 25

data['leaderboard'] = [
	{"name": "Avg. Number of Shapes Used", "value": shapes_used, "order": "asc"},
	{"name": "Avg. Execution Time", "value": time, "order": "asc"},
	{"name": "Avg. Number of Colors Used", "value": colors_used, "order": "asc"},
	{"name": "Avg. Number of Unfilled Cells", "value": int(unfilled_cells), "order": "asc"}
]

with open('../results/results.json', 'w') as f:
    json.dump(data, f)
