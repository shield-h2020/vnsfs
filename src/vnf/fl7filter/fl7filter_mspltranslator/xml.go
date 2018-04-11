package main

import (
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/lestrrat/go-libxml2/parser"
	"github.com/lestrrat/go-libxml2/xsd"
	"vnsfmspl"
)

const (
	STARTING_ID = 4300000 // starting ID for custom  Rules
)

func ValidateXML(xmlFile *os.File) int {
	ruleID = STARTING_ID
	xmlSchema, err := ioutil.ReadFile(*xml_schema)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Can't open " + *xml_schema)
		return 1
	}

	p := parser.New()
	// Parse XSD
	xsdFile, err := xsd.Parse(xmlSchema)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Can't parse " + *xml_schema)
		return 1
	}
	defer xsdFile.Free()

	var valid bool
	valid = true
	xmlBytes, err := ioutil.ReadAll(xmlFile)
	if err != nil {
		fmt.Println(err)
		return 1
	}
	doc, err := p.Parse(xmlBytes)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Can't parse input XML")
		return 1
	}

	if err := xsdFile.Validate(doc); err != nil {
		for _, e := range err.(xsd.SchemaValidationError).Errors() {
			fmt.Println(e)
			valid = false
		}
	}

	if valid == false {
		fmt.Println("Invalid XML")
		return 1
	} else {
		fmt.Println("Valid XML")
		return 0
	}
}

func ParseXML(xmlFile *os.File) ([]vnsfmspl.VirtualHost, int) {
	// change this to write config for different WAFs
	selected_waf := ModSecurity{}

	// I borrowed a typical Apache term to represent different backend servers
	vhs := []vnsfmspl.VirtualHost{}

	// start parsing XML
	var root vnsfmspl.TMsplHyphenSet
	if err := xml.NewDecoder(xmlFile).Decode(&root); err != nil {
		fmt.Println(err)
		return nil, 1
	}

	// one single it_resource per XML
	it_resource := root.TItHyphenResource

	// one single configuration per XML
	configuration := it_resource.TConfiguration

	// parse rules
	rules := configuration.TRule

	for k, _ := range rules {
		total = total + 1

		vh := vnsfmspl.VirtualHost{}
		rc := vnsfmspl.RuleConfig{}
		sc := vnsfmspl.SslConfig{}
		al := vnsfmspl.ApplicationLayerConfig{}

		rc.SourceAddress = rules[k].TSourceHyphenAddress.Text
		rc.SourcePort = rules[k].TSourceHyphenPort.Text
		rc.DomainName = rules[k].TDestinationHyphenDomain.Text

		// create an array of paths
		paths := make([]vnsfmspl.PathConfig, len(rules[k].TPaths.TPath))
		for j, v1 := range rules[k].TPaths.TPath {
			pc := vnsfmspl.PathConfig{}

			pc.DestinationAddress = v1.TDestinationHyphenAddress.Text
			pc.DestinationPort = v1.TDestinationHyphenPort.Text
			pc.InputPath = v1.TPathHyphenDir.Text
			pc.DestinationPath = v1.TDestinationHyphenPath.Text
			pc.DestinationProtocol = v1.TDestinationHyphenProtocol.Text

			// SSL config may change according to reverse proxy config

			if v1.TSsl.TStatus.Text == vnsfmspl.ENABLED_VALUE {
				sc.Status, sc.CertificatePath, sc.PrivatePath = vnsfmspl.WriteSSLEnabledRule(selected_waf,
					v1.TSsl.TStatus.Text, v1.TSsl.TCertificateHyphenPath.Text, v1.TSsl.TPrivateHyphenPath.Text)
			}
			pc.Ssl = sc

			// start application layer option parsing
			// set a temporary variable to avoid very long statements
			app_layer := v1.TCondition.TApplicationHyphenLayerHyphenCondition

			// enable/disable waf
			al.Action = vnsfmspl.GetStatus(selected_waf, app_layer.TStatus.Text)

			// see default-response XML element
			al.DefaultResponse = app_layer.TDefaultHyphenResponse.Text

			// see request-body-inspection XML element
			if app_layer.TRequestHyphenBodyHyphenInspection != nil {
				al.RequestBodyInspection = vnsfmspl.WriteRequestBodyEnabledRule(selected_waf, app_layer.TRequestHyphenBodyHyphenInspection.Text)
			}

			// see request-body-limit XML element
			if app_layer.TRequestHyphenBodyHyphenLimit != nil {
				al.RequestBodyLimit = vnsfmspl.WriteRequestBodyLimitRule(selected_waf, app_layer.TRequestHyphenBodyHyphenLimit.Text)
			}

			// see response-body-inspection XML element
			if app_layer.TResponseHyphenBodyHyphenInspection != nil {
				al.ResponseBodyInspection = vnsfmspl.WriteResponseBodyEnabledRule(selected_waf, app_layer.TResponseHyphenBodyHyphenInspection.Text)
			}

			// collection of custom rules not in Rules Map
			al.AddedRules = []string{}

			// block IPs
			for _, v2 := range app_layer.TBlockHyphenIp {
				ruleID++
				tmp := vnsfmspl.WriteBlockIPRule(selected_waf, v2.Text, ruleID)
				al.AddedRules = append(al.AddedRules, tmp)
			}

			// restrict paths
			for _, v2 := range app_layer.TRestrict {
				ruleID++
				tmp := vnsfmspl.WriteRestrictPathRule(selected_waf, v2.Text, ruleID)
				al.AddedRules = append(al.AddedRules, tmp)
			}

			// rules in base64
			for _, _ = range app_layer.TRawHyphenRule {
				// TODO
			}

			// array of elements
			wafrules := []string{}
			for _, j1 := range app_layer.TPattern {
				// check if there is the ALL condition
				if j1.TName.Text == "ALL" && j1.TStatus.Text == "ENABLED" {
					for _, v11 := range vnsfmspl.Rules {
						for v12 := range v11 {
							filename := *waf_rulepath + v11[v12]
							if contains(wafrules, filename) == true {
								continue
							}
							wafrules = append(wafrules, filename)
						}
					}
				}

				rule_file := vnsfmspl.Rules[j1.TName.Text]
				if j1.TStatus.Text == "ENABLED" {
					// add files associated with that rule
					for l := range rule_file {
						filename := *waf_rulepath + rule_file[l]
						if contains(wafrules, filename) == true {
							continue
						}
						wafrules = append(wafrules, filename)
					}
				}
			}
			al.Rules = wafrules
			// end application layer options

			pc.ApplicationLayer = al
			paths[j] = pc
		}
		// WAF default reponse if there is a match

		rc.Paths = paths
		vh.Rule = rc
		vhs = append(vhs, vh)
	}
	return vhs, 0
}
