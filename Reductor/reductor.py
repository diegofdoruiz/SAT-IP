#!/usr/bin/env python3
import os
class Reductor(object):
	"""docstring for ClassName"""
	def __init__(self):
		self.number_of_variables = 0
		self.number_of_clauses = 0
		self.file = None

	def createFile(self, old_file):
		old_file_name = os.path.basename(old_file)
		old_file_name = old_file_name.split(".cnf")
		new_file_name = old_file_name[0] + ".mzn"
		print('Writing '+new_file_name+' file')
		self.file = open('../InstanciasMiniZinc/'+new_file_name, "w")
		self.file.write("% Instancia MiniZinc\n")
		self.file.write("% "+new_file_name+"\n")
		self.file.write("\n")

	def writeVariables(self):
		self.file.write("% SAT variables\n")
		for var in range(1,self.number_of_variables+1):
			self.file.write("var 0..1: v"+str(var)+";\n")
		self.file.write("\n")

	def writeAdditionalVariables(self):
		self.file.write("% Additional variables for IP\n")
		for var in range(1,self.number_of_variables+1):
			self.file.write("var 0..1: n_v"+str(var)+";\n")
		self.file.write("\n")

	def writeConstraintsVariables(self):
		#SAT Constraints 0 <= vi <= 1
		self.file.write("% Constraints Between 0 and 1 for SAT variables\n")
		for var in range(1,self.number_of_variables+1):
			self.file.write("constraint v"+str(var)+" >= 0 /\\ v"+str(var)+" <= 1;\n")
		self.file.write("\n")

		#IP Constraints 0 <= n_vi <= 1
		self.file.write("% Constraints Between 0 and 1 for IP variables\n")
		for var in range(1,self.number_of_variables+1):
			self.file.write("constraint n_v"+str(var)+" >= 0 /\\ n_v"+str(var)+" <= 1;\n")
		self.file.write("\n")

		# Constraints 1 <= vi + n_vi <= 1
		self.file.write("% Constraints 1 <= vi + n_vi <= 1 all variables\n")
		for var in range(1,self.number_of_variables+1):
			self.file.write("constraint 1 <= v"+str(var)+" + n_v"+str(var)+" /\\ v"+str(var)+" + n_v"+str(var)+" <= 1;\n")
		self.file.write("\n")

	def writeOneClauseConstraint(self, line_tokens):
		self.file.write("constraint ")
		for i in range(0, len(line_tokens)):
			if i == len(line_tokens)-1:
				self.file.write(" >= 1;")
			else:			
				if int(line_tokens[i]) > 0:
					if i == len(line_tokens)-2:
						self.file.write("v"+line_tokens[i])
					else:
						self.file.write("v"+line_tokens[i]+" + ")
				elif int(line_tokens[i]) < 0:
					if i == len(line_tokens)-2:
						self.file.write("n_v"+str(abs(int(line_tokens[i]))))
					else:
						self.file.write("n_v"+str(abs(int(line_tokens[i])))+" + ")
		self.file.write("\n")

	def resetGlobalVariables(self):
		self.number_of_variables = 0
		self.number_of_clauses = 0
		self.file = None

	def mainFunction(self):
		path = '../InstanciasSAT/'
		files = []
		#r=root, d=directories, f = files
		print('-----------------------------------------------------')
		print('--------------------- SAT to IP ---------------------')
		print('-----------------------------------------------------\n')
		print('***** Cargando archivos *****\n')
		for r, d, f in os.walk(path):
			for file in f:
				if '.cnf' in file:
					files.append(os.path.join(r, file))

		for old_file in files:
			# Open the file with read only permit
			f = open(old_file)

			# use readline() to read the first line 
			line = f.readline()

			init_clauses = False
			counter = 0

			print('Leyendo archivo '+old_file)

			# use the read line to read further.
			# If the file is not empty keep reading one line
			# at a time, till the file is empty
			while line:
			    # split line 
			    tokens = line.split()
			    # Read number of variables and number of clauses
			    if len(tokens) != 0 and tokens[0] in ("p"):
			
			    	# number of variables
			    	self.number_of_variables = int(tokens[2])

			    	# number of clauses
			    	self.number_of_clauses = int(tokens[3])
			    	
			    	print('Variables: '+tokens[2]+' Clauses: '+tokens[3])

			    	# Variables, Constraints for variables
			    	self.createFile(old_file)
			    	self.writeVariables()
			    	self.writeAdditionalVariables()
			    	self.writeConstraintsVariables()
			    elif len(tokens) != 0 and tokens[0] not in ("p", "c"):
			    	counter = counter + 1
			    	if counter%50 == 0:
			    		print('.', end='')
			    	if not init_clauses:
			    		self.file.write("% Constraints SAT clauses\n")
			    		init_clauses = True
			    	# write one SAT clause constraint for this line
			    	if len(tokens)>0:
			    		self.writeOneClauseConstraint(tokens)

			    # use realine() to read next line
			    line = f.readline()
			self.file.write("%  Function\n")
			self.file.write("solve satisfy;")
			self.file.close()
			f.close()
			self.resetGlobalVariables()
			print('\n')


if __name__ == "__main__":
    reductor = Reductor()
    reductor.mainFunction()