# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:29:28 2023

@author: S4
"""

import pickle
import pandas as pd
import os
#import chatgtp3_5_test as gpt
#import gpt_4_test as gpt
import ollama_test as llms
import time
import prompt_p

def main(question_tpye,dataset,infor,model_name,cate):
	folder_name = "output_data/%s/answers_%s_%s_%s%s/"%(model_name,dataset,question_tpye,"infor" if infor else "noninfor","" if cate else "_int")
	os.makedirs(folder_name,exist_ok=True)
	f = open("%s/questions_%s%s.pkl"%(dataset,question_tpye,"" if cate else "_int"),'rb')
	questions = pickle.load(f)
	f.close()
	print("===================Start GPT answers=====================")
	answers = pd.DataFrame(columns=["participantid","answer"])
	exist_list = os.listdir(folder_name)
	failed_id = []
	failed_es = []
	for i in range(len(questions)):
		if not (questions["participantid"][i]+".txt" in exist_list):
			try:
				answer = llms.get_answer(questions["question"][i],model_name)
				df = pd.DataFrame([[questions["participantid"][i],answer]],
							columns = ["participantid","answer"])		
				answers = pd.concat([answers,df],ignore_index=True)
				f = open(folder_name+"%s.txt"%(questions["participantid"][i]),"w")
				f.write(answer)
				f.close()
			except Exception as es:
				failed_id.append(questions["participantid"][i]);failed_es.append(es)
				#print("Start sleeping....");time.sleep(900);i=i-1#for gpt4 only
				print("%s \n %s"%(es,questions["participantid"][i]))
			#for gpt4 only
			print("=================== %s ====================="%(str(i).rjust(3,"0")))			
	f = open('answers_%s.pkl'%question_tpye,'wb')
	pickle.dump({"answers":answers,
			  "failed_id":failed_id,
			  "failed_es":failed_es}, f)
	f.close()
	
if __name__ == "__main__":	
	question_tpyes = ["factors","facets","facets_factors","factors_all"]
	dataset = "prolific"
	model_name = "gemma2"
	info = True
	cate = True
	if dataset=="prolific":
		question_tpyes=[question_tpyes[3]]
	for question_tpye in question_tpyes:
		prompt_p.save_questions(question_tpye,dataset,info,cate)
		f = open("%s/questions_%s.pkl"%(dataset,question_tpye),"rb")
		q = pickle.load(f)
		f.close()
		main(question_tpye,dataset,info,model_name,cate)