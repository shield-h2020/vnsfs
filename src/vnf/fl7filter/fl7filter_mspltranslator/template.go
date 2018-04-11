package main

import (
	"bytes"
	"fmt"
	"os"
	"text/template"

	"vnsfmspl"
)

var ruleID int // ID abailables for reservation

type BlockIP struct {
	IP     string
	RuleID int
}

type BlockPath struct {
	Path   string
	RuleID int
}

func WriteTemplate(vh *vnsfmspl.VirtualHost) int {
	template, err := template.ParseFiles(*template_file)
	if err != nil {
		fmt.Println(err)
		return 1
	}

	// create output buffer
	buffer := new(bytes.Buffer)
	template.Execute(buffer, vh)
	fmt.Println(buffer.String()) // optional -> Print template in stdout

	output_file_name := ""
	if total == 1 {
		output_file_name = "default-site.conf"
	} else {
		output_file_name = "virtual_host_" + vh.Rule.DomainName + ".conf"
	}

	// open destination file
	file, err := os.Create(*output_path + output_file_name)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Can't open ", output_file_name)
		return 1
	}
	defer file.Close()

	// write bytes to output file
	bytes_written, err := file.Write(buffer.Bytes())
	if err != nil || bytes_written != buffer.Len() {
		fmt.Println(err)
		return 1
	}
	return 0
}
