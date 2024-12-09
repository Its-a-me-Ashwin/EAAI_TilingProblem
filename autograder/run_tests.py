import os
import sys
import json
import numpy as np

def checkGrid(grid):
    # Check that no adjacent cells have the same color
    for i in range(len(grid)):
        for j in range(len(grid)):
            color = grid[i, j]
            if i > 0 and grid[i - 1, j] == color:
                return False
            if i < len(grid) - 1 and grid[i + 1, j] == color:
                return False
            if j > 0 and grid[i, j - 1] == color:
                return False
            if j < len(grid) - 1 and grid[i, j + 1] == color:
                return False

    return True


###############################################################################

os.chdir('submission/')
sys.path.append("./")
score = 0
cont = 1

try:
	os.system('rm shapes.txt time.txt grid.txt')
except:
	pass

data={}

###############################################################################

try:
	lines = open('hw1.py').readlines()
except:
	print("Error loading the hw1.py file - please ensure both hw1.py and gridgame.py files were uploaded, and not renamed. Please make sure you did not upload a zipped directory containing the files.")
	cont = 0

if cont==1:
	i = 0
	l = 0
	count = 0
	for line in lines:
		if 'ShapePlacementGrid' in line and i==0:
			i=l
			count+=1
		elif 'ShapePlacementGrid' in line:
			count+=1
		l+=1
	if count>1:
		print("Error: Multiple instances of 'ShapePlacementGrid' function found in hw1.py - please remove all duplicate instances, retaining only the call on line 17 in the skeleton code.")
		cont = 0

	if cont==1:
		line_i_temp = lines[i].split('GUI')
		lines[i] = ''.join([line_i_temp[0],"GUI = False, render_delay_sec = 0.0, gs = 9, num_colored_boxes=8)\n"])

		f=open('hw1_test_1.py', 'w')
		f.write(''.join(lines))
		f.close()

		try:
			os.system('python3 hw1_test_1.py')
		except:
			print("Error running the hw1.py file - see stdout.")
			cont = 0

		if cont==1:

			try:
				init_grid = np.loadtxt('initial_grid.txt', dtype=int)
				time_1 = float(open('time.txt', 'r').readlines()[0].rstrip())
				shape_lines = open('shapes.txt', 'r').readlines()[0]
				grid = np.loadtxt('grid.txt', dtype=int)
			
			except:
				print("Error loading one or more output files (initial_grid.txt, time.txt, shapes.txt, grid.txt) - please ensure the output files are being generated correctly.")
				cont = 0

			if cont==1:
				shape_lines = shape_lines.rstrip(')]').lstrip('[(').split('), (')
				shape_list = []

				for shape in shape_lines:
					sl = []
					shape_info = shape.split(', ')
					sl += [int(shape_info[0]), ]
					sl += [[int(shape_info[1].lstrip('[')), int(shape_info[2].rstrip(']'))], ]
					sl += [int(shape_info[3]), ]
					shape_list += [sl, ]

				shapes_used_1 = len(shape_list)
				additional_colors_used_1 = len(np.unique(grid[grid!=-1])) - len(np.unique(init_grid[init_grid!=-1]))
				unfilled_cells_frac_1 = np.mean(grid==-1)
				valid_coloring_1 = checkGrid(grid)

###############################################################################

try:
	os.system('rm shapes.txt time.txt grid.txt')
except:
	pass

if cont==1:

	lines[i] = ''.join([line_i_temp[0],"GUI = False, render_delay_sec = 0.0, gs = 11, num_colored_boxes=15)\n"])
	f=open('hw1_test_2.py', 'w')
	f.write(''.join(lines))
	f.close()

	try:
		os.system('python3 hw1_test_2.py')
	except:
		print("Error running the hw1.py file - see stdout.")
		cont = 0

	if cont==1:

		try:
			init_grid = np.loadtxt('initial_grid.txt', dtype=int)
			time_2 = float(open('time.txt', 'r').readlines()[0].rstrip())
			shape_lines = open('shapes.txt', 'r').readlines()[0]
			grid = np.loadtxt('grid.txt', dtype=int)
		
		except:
			print("Error loading one or more output files (initial_grid.txt, time.txt, shapes.txt, grid.txt) - please ensure the output files are being generated correctly.")
			cont = 0

		if cont==1:
			shape_lines = shape_lines.rstrip(')]').lstrip('[(').split('), (')
			shape_list = []

			for shape in shape_lines:
				sl = []
				shape_info = shape.split(', ')
				sl += [int(shape_info[0]), ]
				sl += [[int(shape_info[1].lstrip('[')), int(shape_info[2].rstrip(']'))], ]
				sl += [int(shape_info[3]), ]
				shape_list += [sl, ]

			shapes_used_2 = len(shape_list)
			additional_colors_used_2 = len(np.unique(grid[grid!=-1])) - len(np.unique(init_grid[init_grid!=-1]))
			unfilled_cells_frac_2 = np.mean(grid==-1)
			valid_coloring_2 = checkGrid(grid)

###############################################################################

if cont == 1:
	if valid_coloring_1==False or valid_coloring_2==False:
		print("Error: One or more colorings are invalid (i.e., violates constraints) - please ensure that no adjacent cells have the same color, and test over several random initializations.")
		data["score"] = 0
	
	else:
		avg_add_colors_used = 0.5*additional_colors_used_1 + 0.5*additional_colors_used_2
		avg_unfilled_cells = 0.5*unfilled_cells_frac_1 + 0.5*unfilled_cells_frac_2
		avg_shapes_used = 0.5*shapes_used_1 + 0.5*shapes_used_2
		total_time = time_1 + time_2

		shape_multiplier = 1 if avg_shapes_used <= 50 else np.exp(-1/1500000*avg_shapes_used**3)

		data["score"] = 35 * (1 - avg_unfilled_cells) * (1 - max(avg_add_colors_used-1, 0)/3) * shape_multiplier
		
		# second last term penalizes for using more than 1 additional color - no penalty for using 1 additional color, and then decays to 0 as the number of additional colors used increases.

		# last term in the above equation is a penalty multiplier (between 0-1) term for using too many shapes - no penalty until 50 shapes, and then the multiplier decays to 0 as the number of shapes used increases. Based on total number of empty cells (179) for both test cases combined.

	data["visibility"] = "visible"
	data["stdout_visibility"] = "visible"

	try:
		data['leaderboard'] = [
			{"name": "Avg. Number of Shapes Used", "value": int(avg_shapes_used), "order": "asc"},
			{"name": "Avg. Execution Time", "value": total_time, "order": "asc"},
			{"name": "Avg. Number of Additional Colors Used", "value": int(avg_add_colors_used), "order": "asc"},
			{"name": "Avg. Number of Unfilled Cells", "value": int(avg_unfilled_cells), "order": "asc"}
		]
	except:
		pass


else:
	print("Please resolve the errors above and resubmit.")
	data["score"] = 0
	data["visibility"] = "visible"
	data["stdout_visibility"] = "visible"

with open('../results/results.json', 'w') as f:
    json.dump(data, f)