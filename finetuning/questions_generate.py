# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:29:28 2023

@author: S4
"""

import pickle
import pandas as pd
import os
#import chatgtp4_test as gpt
#import gpt_4_test as gpt
import time
import sys 
sys.path.append("..") 
import data_analysis
import ollama_test
import numpy as np

def phrase_ground_truth(transcript,data,question_tpye,dataset,cate):
	#g_d: the list for col names of the ground truth, [Extraversion, Conti]
	question_tpyes = ["factors","facets","factors_all","hirability","mean_facets"]
	n = question_tpyes.index(question_tpye)
	m = 0 if n>=4 else n
	d2 = data["ground_truth_%s"%dataset].columns
	ground_truth = data["ground_truth_%s"%dataset]
	if dataset=="opva":
		sc = [ [["Extraversion_observer_facet_mean","Conscientiousness_observer_facet_mean"],#observer reported
			      ["extra10","consc10"]],#self-reported 
			   [d2[188:196],d2[118:126],d2[134:142], d2[150:158], d2[166:174],d2[444:452]],#facets
			   [d2[182:188],d2[112:118]],#all factors, mean_observer_rating, self-rating
			   [d2[210:215]]]#hirablity score		
		sc_pre = [["Extraversion","Conscientiousness"],
			  ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism'],
			  ["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"],
			  ['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']]
	else:
		sc = [[['A_observer','C_observer','H_observer','E_observer'],['A_self', 'C_self', 'H_self','E_self']],
				[],
				[d2[17:23],d2[11:17]],#all factors
				[d2[23:29],d2[29:]]#generic and persoanlity question ratings
				]
		sc_pre = [["Agreeableness","Conscientiousness","Honesty-Humility","Extraversion"],
			[],["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"]]
	if not cate:
		ground_truth = data_analysis.convert_columns(ground_truth,sc)		
		sc = [[[element + "_int" for element in sublist] for sublist in inner_list] for inner_list in sc]
		data["ground_truth_%s"%dataset] = ground_truth
	select_col_tru = sc[m][0]
	select_col_pre =sc_pre [m]
	tru_data = ground_truth[[ground_truth.columns[0]]+select_col_tru]
	t = tru_data[tru_data[tru_data.columns[0]]==transcript[0]]
	if t.shape[0]==0:
		text = np.nan
	else:
		if cate:
			text = t.apply(lambda row: '\n'.join(f"{select_col_pre[i]}: {row[col]}" for i,col in enumerate(t.columns[1:])), axis=1).iloc[0]
		else:
			score_dict = {0:'low',1:'medium',2:'high'}
			try:
				text = t.apply(lambda row: '\n'.join(f"{select_col_pre[i]}: {score_dict[row[col]]}" for i,col in enumerate(t.columns[1:])), axis=1).iloc[0]
			except:
				text = np.nan
		'''
		text = []
		for i in range(1,t.shape[1]):
			if cate:
				text.append("%s: %s\n"%(select_col_pre[i-1]),str(round(float(t.iloc[0,i]),1)))
			else:
				text.append("%s: %s\n"%(select_col_pre[i-1],str(score_dict[t.iloc[0,i]])))
		'''		
	return text
	
def question(transcript,data,question_tpye,dataset,infor,cate):
	#question_tpye = "factors", "facets" (only for opva),"mean_facets","none","generic_only"(only for prolific)
	#dataset = "opva" or "prolific"
	#infor =True, tell the AI what is this question is about
	ratings = phrase_ground_truth(transcript,data,question_tpye,dataset,cate)
	meta = data["meta_%s"%(dataset)]
	num = meta["num_factors"] if (question_tpye == "factors" or question_tpye == 'mean_facets') else meta["num_facets"]	
	t1 = "For each question, I can give you the indication about what is the corresponding %s this question is related to. "%(question_tpye[0:-1] if question_tpye !="mean_facets" else "facect")
	t2 = "The person also answer 2 generic questions which do not relate to a specific factor of personality. You can also use this information to rate his or her personality."
	keys = ', '.join(list(set([i for i in meta["questions_key_personality"].values()]))) if (question_tpye == "factors" or question_tpye == 'mean_facets') else ', '.join(list(set([i for i in meta["questions_key_facet"].values()])))
	head = "You are a psychologist in personality research. This personlity scores of this individual was rated based on his/her answers to following questions.\n%s\nCould you first analyze the individual’s answers and then explain why he/she was rated like this? The personality scores (%s) were rated according to the HEXACO personality model by %s %s (i.e., %s). %s%s"%(ratings,"ranging from 1.0-5.0" if cate else "high/medium/low",num,question_tpye if question_tpye !="mean_facets" else "factors",
			keys,t1 if infor else "", t2 if dataset=="prolific" and question_tpye!="generic_only" else "")
	head = head+"\n"
	qList = ["q%s"%(i) for i in range(1,len(meta["questions"])+1)]
	body = []
	for q in qList :
		q_infor = "\nThis is a question related to the %s of %s."%(question_tpye[0:-1] if question_tpye !="mean_facets" else "facet" ,meta["questions_key_personality"][q] if question_tpye == "factors" else meta["questions_key_facet"][q])
		txt = "Question %s: %s\nAnswer: %s%s\n"%(q[1],meta["questions"][q],transcript[q],q_infor if infor else "")
		body.append(txt)
	#tail = "Please answer with the template of ratings: \n and why."
	tt = list(set([i for i in meta["questions_key_personality"].values()])) if (question_tpye == "factors" or question_tpye == 'mean_facets') else list(set([i for i in meta["questions_key_facet"].values()]))
	temp = ""
	for t in tt:
		temp = temp + t+": rating \n"
	tail  = "In the explanation, do not mention the related questions."
	#tail = "Please answer with the template:\n"+ temp + "and why. The rating should be overall ratings instead of for each question."
	#tail_ = "Please rate just 2 factors (i.e., Extraversion and Conscientiousness) instead of the 8 facets. "
	#if question_tpye == "mean_facets":
		#tail = tail_+ tail
	text = head +"".join(body)+tail
	return text

def phrase_questions(transcripts,data,question_tpye,dataset,infor,cate):
	#questions = pd.DataFrame(columns=["participantid","question"])
	#for transcript in transcripts:
	rows = []
	for i in range(len(transcripts)):
		transcript = transcripts.loc[i]
		text = question(transcript,data,question_tpye,dataset,infor,cate)
		'''
		df = pd.DataFrame([[transcript["participantid"],text]],
					columns = ["participantid","question"])
		'''
		rows.append({"participantid": transcript["participantid"], "question": text})
		#questions = pd.concat([questions,df],ignore_index=True)
		sys.stdout.write(f"\r{i}/{len(transcripts)}")
		sys.stdout.flush()
	questions = pd.DataFrame(rows)
	questions = questions.dropna()
	return questions

def save_questions(question_tpye,dataset,infor,cate):
	f = open('../data.pkl','rb')
	data = pickle.load(f)
	f.close()
	transcripts = data["transcripts_%s"%dataset]
	questions = phrase_questions(transcripts,data,question_tpye,dataset,infor,cate)
	f = open('%s/questions_%s.pkl'%(dataset,question_tpye),'wb')
	pickle.dump(questions, f)
	f.close()

def main(question_tpye,dataset,model,infor,cate):
	folder_name = "output_data/%s/answers_%s_%s_%s%s/"%(dataset,model,question_tpye,"infor" if infor else "noninfor",""if cate else "_int")
	os.makedirs(folder_name,exist_ok=True)
	f = open("%s/questions_%s.pkl"%(dataset,question_tpye),'rb')
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
				answer = ollama_test.get_answer(questions["question"][i],model)
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
	question_tpyes = ["factors","facets","mean_facets"]
	question_tpye = question_tpyes[0]
	dataset = "opva"
	infor = True
	cate = False
	model = "gemma2"
	#for question_tpye in question_tpyes:
	save_questions(question_tpye,dataset,infor,cate)
	main(question_tpye,dataset,model,infor,cate)
	'''
	dataset = "opva"
	predict = get_answers(question_tpye,dataset)   
	f = open("output_data/pre_opva_factors_infor.pkl",'wb')
	pickle.dump(predict,f)
	f.close()
	f = open("%s/questions_%s.pkl"%(dataset,question_tpye),"rb")
	q = pickle.load(f)
	f.close()	
	'''
