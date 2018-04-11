package main

import "os"

func contains(array []string, input string) bool {
	for _, j := range array {
		if input == j {
			return true
		}
	}
	return false
}

func close(file *os.File) {
	if err := file.Close(); err != nil {
		panic(err)
	}
}
