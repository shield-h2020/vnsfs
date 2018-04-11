#!/bin/bash
tar zcf MSPLTranslatorDocker.tar Dockerfile mspltranslator template_virtualhost mspl_schema_mod.xsd
rm -rf ../vNSF_Controller/MSPLTranslatorDocker
rm -rf ../tests/vnsf_data/MSPLTranslatorDocker
mkdir -p ../vNSF_Controller/MSPLTranslatorDocker
mkdir -p ../tests/vnsf_data/MSPLTranslatorDocker
cp MSPLTranslatorDocker.tar ../vNSF_Controller/MSPLTranslatorDocker/
cp MSPLTranslatorDocker.tar ../tests/vnsf_data/MSPLTranslatorDocker
rm MSPLTranslatorDocker.tar
