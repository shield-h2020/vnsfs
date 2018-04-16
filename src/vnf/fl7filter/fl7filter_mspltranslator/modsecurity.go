package main

import (
	"bytes"
	"text/template"

	"vnsfmspl"
)

type ModSecurity struct{}

func (ModSecurity) Status(value string) string {
	if value == vnsfmspl.ENABLED_VALUE {
		return "On"
	} else if value == vnsfmspl.DETECTION_VALUE {
		return "DetectionOnly"
	} else if value == vnsfmspl.DISABLED_VALUE {
		return "Off"
	}
	return vnsfmspl.DEFAULT
}

func (ModSecurity) WriteBlockIP(IP string, ruleID int) string {
	tmpl, err := template.New("BlockIPRule").Parse(`SecRule REMOTE_ADDR "@ipMatch {{.IP}}" "id:'{{.RuleID}}',deny,msg:'Detected Bad IP'"`)
	if err != nil {
		panic(err)
	}
	tmp := BlockIP{IP, ruleID}
	buffer := new(bytes.Buffer)
	err = tmpl.Execute(buffer, &tmp)
	if err != nil {
		panic(err)
	}
	return buffer.String()
}

func (ModSecurity) WriteRestrictPath(Path string, ruleID int) string {
	tmpl, err := template.New("BlockPathRule").Parse(`SecRule REQUEST_URI "{{.Path}}" "id:'{{.RuleID}}',phase:1,deny,msg:'Attempt to access restricted path'"`)
	if err != nil {
		panic(err)
	}
	tmp := BlockPath{Path, ruleID}
	buffer := new(bytes.Buffer)
	err = tmpl.Execute(buffer, &tmp)
	if err != nil {
		panic(err)
	}
	return buffer.String()
}

func (ModSecurity) WriteRequestBodyEnabled(value string) string {
	tmpl, err := template.New("RequestBodyEnabledRule").Parse(`SecRequestBodyAccess {{.}}`)
	if err != nil {
		panic(err)
	}

	var tmp string
	if value == vnsfmspl.ENABLED_VALUE {
		tmp = "On"
	} else if value == vnsfmspl.DISABLED_VALUE {
		tmp = "Off"
	} else {
		tmp = "Off"
	}

	buffer := new(bytes.Buffer)
	err = tmpl.Execute(buffer, tmp)
	if err != nil {
		panic(err)
	}
	return buffer.String()
}

func (ModSecurity) WriteRequestBodyLimit(value string) string {
	tmpl, err := template.New("RequestBodyLimitRule").Parse(`SecRequestBodyLimit {{.}}`)
	if err != nil {
		panic(err)
	}
	buffer := new(bytes.Buffer)
	err = tmpl.Execute(buffer, value)
	if err != nil {
		panic(err)
	}
	return buffer.String()
}

func (ModSecurity) WriteResponseBodyEnabled(value string) string {
	tmpl, err := template.New("ResponseBodyEnabledRule").Parse(`SecResponseBodyAccess {{.}}`)
	if err != nil {
		panic(err)
	}
	var tmp string
	if value == vnsfmspl.ENABLED_VALUE {
		tmp = "On"
	} else if value == vnsfmspl.DISABLED_VALUE {
		tmp = "Off"
	}
	buffer := new(bytes.Buffer)
	err = tmpl.Execute(buffer, tmp)
	if err != nil {
		panic(err)
	}
	return buffer.String()
}

func (ModSecurity) WriteSSLEnabled(value string, certificate string, PK string) (string, string, string) {
	var tmp string
	tmpl, err := template.New("SSLengine").Parse(`SSLEngine {{.}}`)
	if err != nil {
		panic(err)
	}

	buffer := new(bytes.Buffer)

	if value == vnsfmspl.ENABLED_VALUE {
		err = tmpl.Execute(buffer, "on")
		if err != nil {
			panic(err)
		}
		tmp = buffer.String()
	} else {
		err = tmpl.Execute(buffer, "off")
		if err != nil {
			panic(err)
		}
		return buffer.String(), "", ""
	}

	// parse certificate path
	tmpl, err = template.New("CertificatePath").Parse(`SSLCertificateFile {{.}}`)
	if err != nil {
		panic(err)
	}

	buffer = new(bytes.Buffer)
	err = tmpl.Execute(buffer, certificate)
	if err != nil {
		panic(err)
	}
	certificate_path := buffer.String()

	// parse PrivateKey path
	tmpl, err = template.New("PrivateKeyPath").Parse(`SSLCertificateKeyFile {{.}}`)
	if err != nil {
		panic(err)
	}

	buffer = new(bytes.Buffer)
	err = tmpl.Execute(buffer, PK)
	if err != nil {
		panic(err)
	}
	private_key_path := buffer.String()

	return tmp, certificate_path, private_key_path

}
