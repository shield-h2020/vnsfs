#!/usr/bin/python

"""
Usage:
 chopper-SHIELD.py (forensic | realtime) -t <file> -n <file> -k <argument> -l <argument>
 chopper-SHIELD.py -h | --help

Options:
 -t <file>, --tstat <file>          # Tstat file to be processed
 -n <file>, --network <file>        # Machine Learning trained network
 -k <argument>, --kafka <argument>  # Kafka Topic Name to send the results
 -l <argument>, --limit <argument>  # Time limit to check new directory in tstat path
"""


from docopt import docopt, DocoptExit
from kafka import KafkaProducer
from kafka.errors import KafkaError
import requests
import json
import time
import re
import os
import shutil
import arrow
from datetime import datetime, tzinfo, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from random import randint
from time import sleep
import numpy as np
import logging
import sys
import json
import signal
import warnings
import time

CONFIDENCE      = 0
TIME_START      = 1
TIME_END        = 2
IP_O            = 3
IP_D            = 4
PORT_O          = 5
PORT_D          = 6
PROTOCOL        = 7
TAG             = 8
TAG_NAME        = 9
tagNames=['UNCLASSIFIED','WEB','VIDEO','CLOUD','SSH','CARD SH','VIDEO AUX','CLOUD AUX','ADS']
number_packets_before_send = 4
percentage_threshold_change_alert=0.035
min_prob_confience = 0.75
i_pushed = 0
i_notpushed = 0

LOG_FILENAME = "chopper-SHIELD.log"

class Flow:
        def __init__(self,prob):
            number_of_tags=[0.,0.,0.,0.,0.,0.,0.,0.,0.]
            self.prob=np.array(number_of_tags)
            self.occurrences=np.array(number_of_tags)
            #value,occurrence,index(tag)
            self.last_send=np.array([0.,0.,0.])
            self.times_pushed = 0
            self.add_prob(prob)

            self.time_start = data[28]
            self.time_end = data[29]
            self.ip_o = data[0]
            self.ip_d = data[14]
            self.port_o = data[1]
            self.port_d = data[15]

        def get_number_packets(self):
            return sum(self.occurrences)

        def get_curr_prob(self):
            return np.nan_to_num(self.prob/self.occurrences).max()

        def get_curr_tag(self):
            return np.argmax(np.nan_to_num(self.prob/self.occurrences))

        def get_last_prob_sended(self):
            return self.last_send[0]

        def get_last_tag_sended(self):
            return self.last_send[2]

        def add_prob(self,prob):
            self.prob[np.argmax(prob)] += max(prob)
            self.occurrences[np.argmax(prob)] += 1

        def update_last_sended(self):
            self.last_send = np.array([self.get_curr_prob(), self.occurrences[np.argmax(np.nan_to_num(self.prob/self.occurrences))], np.argmax(np.nan_to_num(self.prob/self.occurrences))])
            self.times_pushed += 1

        def __str__(self):
            return '[{:<15}] {:<15}:{:<5} > {:<15}:{:<5}\tProb: [ {:<10.4}{:<10.4}{:<10.4} ]\t#Ocurrences: [ {:<6.4}{:<6.4}{:<4.4} ]\tLastSend: [ {:<6.4}{:<6.4}{:<4.4} ]\tTimes_Pushed: {}'.format(self.time_start,self.ip_o,self.port_o,self.ip_d,self.port_d, (self.prob/self.occurrences)[0], (self.prob/self.occurrences)[1], (self.prob/self.occurrences)[2],self.occurrences[0],self.occurrences[1],self.occurrences[2],self.last_send[0],self.last_send[1],self.last_send[2],self.times_pushed)

def get_output_message(flow):
    return "PREDICTION: {:<8}PROBABILITY: {:<8.4}TIMES_PUSHED: {:<8}ALL_PROBS: [ {:<6.4}{:<6.4}{:<4.4} ]\t\t[{}] {:<15}:{:<5} > {:<15}:{:<5} ({:<5})\tPushed: {:<7}Not Pushed: {}".format(flow.get_curr_tag(), flow.get_curr_prob(),int(flow.times_pushed),str(flow.prob[0]/flow.occurrences[0]),str(flow.prob[1]/flow.occurrences[1]),str(flow.prob[2]/flow.occurrences[2]),'%.0f'%float(data[28]),data[0],data[1],data[14],data[15],int(flow.get_number_packets()),i_pushed,i_notpushed)



def publish_flow_to_kafka(flow, producer, topicName):
    """
    This function publish a new flow in the Kafka bus to Apache Spot
    """
    document = dict()

    if flow.get_curr_prob() < min_prob_confience:
        ML_score=str(flow.get_curr_prob())
        tag='9'
        tagName=str('Other')
    else:
        ML_score=str(flow.get_curr_prob())
        tag=str(flow.get_curr_tag())
        tagName=str(tagNames[flow.get_curr_tag()])

    #document['flow_id']=data[0]+data[1]+data[14]+data[15]+'%.0f'%float(data[28])
    treceived='%.0f'%float(data[28])
    dip=str(data[14])
    sport=str(data[1])
    dport=str(data[15])
    proto='TCP'
    flag='0'
    ipkt=str(data[7])
    ibyt=str(data[8])
    opkt=str(data[21])
    obyt=str(data[22])
    input='0'
    output='0'
    rip='0' 

    csv_row= treceived + ',' + dip + ',' + sport + ',' + dport + ',' + proto + ',' + flag + ',' + ipkt + ',' +ibyt+ ','+ opkt + ',' + obyt + ',' +  input + ',' +  output + ',' + rip + ',' + tag + ',' + tagName + ',' + ML_score 

    producer.send(topicName, csv_row)
    flow.update_last_sended()

    if flow.times_pushed == 1 :
        print("(*NEW*) " + get_output_message(flow))
    else:
        print("       " +  get_output_message(flow))


def follow(mode, tstat_file, time_limit):
    
    logging.info("Reading %s file" % tstat_file)
    logfile = open(tstat_file,"r")
    # Read from the begining
    logfile.seek(0,0)
    start_time = time.time()
    while True:
        line = logfile.readline()
        line_split = line.split(" ")
        if "#" in line_split[0]:
            continue

        if not line:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time
            # If not line since time_limit seconds, check tstat output directory
            if elapsed_time > time_limit:
                tstat_dirs = []
                for dirname, dirnames, filenames in os.walk('stdin'):
                    if 'traces00' in dirnames:
                        dirnames.remove('traces00')
                    for subdirectory in dirnames:
                        tstat_dirs.append(subdirectory)
                if len(tstat_dirs) > 1:
                    tstat_dirs.sort()
                    base, old_dir, file = tstat_file.split("/")
                    old_dir_index = tstat_dirs.index(old_dir)

                    if old_dir_index < len(tstat_dirs)-1 :
                        new_dir = tstat_dirs[old_dir_index+1]
                        # Check the last directory is greater than the opened one
                        if new_dir > old_dir:
                            logging.info("New tstat file detected")
                            logfile.close()
                            logging.info("%s successfully closed" %tstat_file)
                            shutil.rmtree("/home/cognet/stdin/" + tstat_dirs[old_dir_index])
                            logging.info("%s has been removed" %tstat_file)
                            if arguments['realtime'] == True:
                                tstat_file = "stdin/" + new_dir + "/log_tcp_temp_complete"
                            elif arguments['forensic'] == True:
                                tstat_file = "stdin/" + new_dir + "/log_tcp_complete"

                            logfile = open(tstat_file,"r")
                            logfile.seek(0,0)
                            logging.info("Reading %s file" %tstat_file)
                start_time =  time.time()
            continue
        else:
            start_time = time.time()
        yield line

def classificator(message, rf, bad_features, good_features, tstat_traces_dic, producer, topicName, mode):
    #for message in tstat_file:
    try:
        global data
        data = message.split()
        y = [data[i] for i in good_features]
        X = np.array(y).reshape(1,-1)
 
	try:
            prob = rf.predict_proba(X)
            prob = prob.tolist()[0]
            prediction = np.argmax(prob)
        except ValueError:
            logging.error("Value Error")

        #key is ip_o,port_o,ip_d,port_d,timeStart
        key = data[0]+data[1]+data[14]+data[15]+'%.0f'%float(data[28])
        try:
            flow = tstat_traces_dic[key]
            flow.add_prob(prob)
            first_ocurrence = False
        except KeyError:
            flow = Flow(prob)
            first_ocurrence = True
           

        # For the real time mode
        if mode == "realtime":
            if (flow.get_curr_prob() > flow.get_last_prob_sended() + percentage_threshold_change_alert) and flow.get_number_packets() >= number_packets_before_send :
       	        global i_pushed
                i_pushed += 1
                publish_flow_to_kafka(flow, producer, topicName)
            else:
                global i_notpushed
                i_notpushed += 1
        elif mode == "forensic":
            publish_flow_to_kafka(flow, producer, topicName)
 
        tstat_traces_dic[key] = flow
    except TypeError:
         logging.error("IO ERROR")
    except IndexError:
         logging.error("Index error")


def initialize(network):

    logging.info("Initializing Network")
    # Create Kafka Producer
    producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
    #Machine Learning Stuff
    #Load model
    logging.info("Loading trained network")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        rf = joblib.load(network)
    logging.info("Trained network successfully loaded")
#    bad_features = [0,1,11,14,15,17,28,29,37,38,39,40,42,49,50,56,57,58,59,60,61,62,63,64,65,66,67,68,69,73,74,79,80,81,83,85,86,87,88,89,90,91,96,97,101,102,103,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130]
    bad_features  = [0,1,3,11,12,13,14,15,17,23,24,25,26,27,28,29,34,37,38,39,40,42,49,50,52,54,56,57,58,59,60,61,62,63,64,65,66,67,68,69,73,74,78,79,80,81,82,83,84,85,86,87,88,89,90,91,96,97,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130]
    bad_features = [i for i in bad_features]
    good_features = [i for i in range(131) if i not in bad_features]
    tstat_traces_dic = { }

    return rf, bad_features, good_features, tstat_traces_dic, producer


def processFile(arguments):
    # Get the parameters from the shell
    tstat_file = arguments['--tstat']
    network = arguments['--network']
    topicName = arguments['--kafka']
    time_limit = int(arguments['--limit'])

    # Initialize the network
    [rf, bad_features, good_features, tstat_traces_dic, producer] = initialize(network)


    if arguments['realtime'] == True:
        mode = "realtime"
    elif arguments['forensic'] == True:
        mode = "forensic"

    # Read tstat_file
    loglines = follow(mode, tstat_file, time_limit)
    for line in loglines:
        classificator(line, rf, bad_features, good_features, tstat_traces_dic, producer, topicName, mode)

if __name__ == '__main__':

	try:
            args=sys.argv;
            args.pop(0)
            arguments = docopt(doc=__doc__, argv=args)
            logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
            processFile(arguments)


        except DocoptExit as e:
            print e.message


