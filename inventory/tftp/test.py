# Python Calculator
# D. Hague


'''# Returns the sum of num1 and num2
def add(num1, num2):
	return num1 + num2


# Returns the subtraction of num1 and num2
def sub(num1, num2):
	return num1 - num2


# multiplies num1 and num2
def mult(num1, num2):
	return num1 * num2


# divides num1 and num2
def div(num1, num2):
	try:
		return num1 / num2
	except ZeroDivisionError:
		print('Do not divide by 0')
		return main()


def expo(num1, num2):
	return num1**num2


def runOp(operation, num1, num2):
	if (operation == '+'):
		print(add(num1, num2))

	if (operation == '-'):
		print(sub(num1, num2))

	if (operation == '*'):
		print(mult(num1, num2))

	if (operation == '/'):
		print(div(num1, num2))

	if (operation == '^'):
		print(expo(num1, num2))'''

class Op:
	# Returns the sum of num1 and num2
	def add(num1, num2):
		return num1 + num2

	# Returns the subtraction of num1 and num2
	def sub(num1, num2):
		return num1 - num2

	# multiplies num1 and num2
	def mult(num1, num2):
		return num1 * num2

	# divides num1 and num2
	def div(num1, num2):
		try:
			return num1 / num2
		except ZeroDivisionError:
			print('Do not divide by 0')
			return main()

	def expo(num1, num2):
		return num1 ** num2

	def runOp(operation, num1: object, num2: object) -> object:
		if (operation == '+'):
			print(Op.add(num1, num2))

		if (operation == '-'):
			print(Op.sub(num1, num2))

		if (operation == '*'):
			print(Op.mult(num1, num2))

		if (operation == '/'):
			print(Op.div(num1, num2))

		if (operation == '^'):
			print(Op.expo(num1, num2))


def main():
	new = True

	while new:
	# for i in range(3):
		operation = input("what do you want to do (+, -, *, /, ^): ")

		if (operation != '+' and operation != '-' and operation != '*' and operation != '/' and operation != '^'):
			# invalid opp check
			print("you must enter a valid operation")
			main()

		else:
			try:
				# entered a valid operation
				num1 = float(input("Enter num1: "))
				num2 = float(input("Enter num2: "))

			except(ValueError):
				print("Enter a valid number... \n(Not a string)")
				main()

		try:
			Op.runOp(operation, num1, num2)

		except(OverflowError):
			print("Number too large... \nCan not compute :(")
			main()

		except(UnboundLocalError):
			print("Don't do dumb stuff next time")
			main()




		# Ask user to continue
		answer = input("would you like to run another calculation? (y for yes, any other value to exit): ")
		if(answer != 'y'):
			# new = False
			break

		else:
			continue


main()
