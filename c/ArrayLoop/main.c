#include <stdio.h>
#include <stdlib.h>


void squareArray(int* array, const int length);

void printArray(const int* const array, const int length);


int main() {
	const int length = 10;
	int array[length];

	for (int i = 0; i < length; i += 1) {
		array[i] = i + 1;
	}

	squareArray(array, length);

	printArray(array, length);

	return 0;
}


void squareArray(int* array, const int length) {
	for (int i = 0; i < length; i += 1) {
		if (array[i] < 5) {
			*array *= *array;
		} else {
			*array = (*array * 2) + 5;
		}
		array++;
	}
}


void printArray(const int* const array, const int length) {
	for (int i = 0; i < length; i += 1) {
		printf("%d\n", array[i]);
	}
}
