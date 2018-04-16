package main

import (
	"flag"
	"fmt"
	"os"
)

var xml_file *string
var template_file *string
var output_path *string
var waf_rulepath *string
var xml_schema *string
var rulepath *string
var total int

func Init() {
	xml_schema = flag.String("xsd", "mspl_schema_mod.xsd", "XSD for mspl input")
	//xml_file = flag.String("input", "/opt/sidecar-docker/sample_rpconfig.xml", "XML file file")
	xml_file = flag.String("input", "mspl.xml", "XML file")
	template_file = flag.String("template", "template_virtualhost", "Template file")
	//output_path = flag.String("path", "/opt/proxy-conf/", "Output Config File Path")
	output_path = flag.String("path", "proxy-conf/", "Output Config File Path")	
	waf_rulepath = flag.String("wafrulepath", "modsecurity.d/activated_rules/", "WAF rule path inside the container")
	flag.Parse()

	if *xml_file == "" {
		fmt.Println("No xml file provided. Exiting...")
		os.Exit(1)
	}
}

func main() {
	Init()
	total = 0 // # of rules

	xmlFile, err := os.Open(*xml_file)
	if err != nil {
		fmt.Println(err)

	}
	defer xmlFile.Close()
	ret := ValidateXML(xmlFile)
	if ret != 0 {
		fmt.Println("Can't validate XML input")
		close(xmlFile)
		os.Exit(1)
	}

	// restore the file pointer
	if val, err := xmlFile.Seek(0, 0); val != 0 || err != nil {
		fmt.Println("Can't seek XML file")
		close(xmlFile)
		os.Exit(1)
	}

	vhs, ret := ParseXML(xmlFile)
	if ret != 0 {
		fmt.Println("Can't parse XML")
		close(xmlFile)
		os.Exit(1)
	}

	for _, vh := range vhs {
		if ret := WriteTemplate(&vh); ret != 0 {
			fmt.Println("Can't write template " + vh.Rule.DomainName)
			close(xmlFile)
			os.Exit(1)
		}
	}
}
