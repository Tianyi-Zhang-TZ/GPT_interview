#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 15:55:34 2023

@author: tianyi
"""

import pickle
import pandas as pd
import pickle
import jsonlines

def question(transcript,meta,question_tpye,dataset,info):
	#question_tpye = "factors", "facets" (only for opva),"facets_factors","none","generic_only"(only for prolific)
	#dataset = "opva" or "prolific"
	#info =True, tell the AI what is this question is about
	num = meta["num_factors"] if (question_tpye == "factors" or question_tpye == 'facets_factors') else meta["num_facets"]
	t1 = "For each question, I can give you the indication (but not strongly constrained by) about what is the corresponding %s this question is related to. "%(question_tpye[0:-1] if question_tpye !="facets_factors" else "facect")
	t2 = "The person also answer 2 generic questions which do not relate to a specific factor of personality. You can also use this information to rate his or her personality."
	keys = ', '.join(list(set([i for i in meta["questions_key_personality"].values()]))) if (question_tpye == "factors" or question_tpye == 'facets_factors') else ', '.join(list(set([i for i in meta["questions_key_facet"].values()])))
	role = "You are a psychologist in personality research. "
	
	head = "Could you rate the personality score of the person based on the answer to the following questions? The personality score (ranging from 1.0-5.0) should be rated according to the HEXCO personality model by %s %s (i.e., %s). %s%s"%(num,question_tpye if question_tpye !="facets_factors" else "factors",
			keys,t1 if info else "", t2 if dataset=="prolific" and question_tpye!="generic_only" else "")
	head = head+"\n"
	qList = ["q%s"%(i) for i in range(1,len(meta["questions"])+1)]
	body = []
	for q in qList :
		q_info = "\nThis is a question related to the %s of %s."%(question_tpye[0:-1] if question_tpye !="facets_factors" else "facet" ,meta["questions_key_personality"][q] if question_tpye == "factors" else meta["questions_key_facet"][q])
		txt = "Question %s: %s\nAnswer: %s%s\n"%(q[1],meta["questions"][q],transcript[q],q_info if info else "")
		body.append(txt)
	#tail = "Please answer with the template of ratings: \n and why."
	tt = list(set([i for i in meta["questions_key_personality"].values()])) if (question_tpye == "factors" or question_tpye == 'facets_factors') else list(set([i for i in meta["questions_key_facet"].values()]))
	temp = ""
	for t in tt:
		temp = temp + t+": rating \n"
	tail = "Please answer with the template:\n"+ temp + "The rating should be overall ratings instead of for each question."
	#tail_ = "Please rate just 2 factors (i.e., Extraversion and Conscientiousness) instead of the 8 facets. "
	#if question_tpye == "facets_factors":
		#tail = tail_+ tail
	text = head +"".join(body)+tail
	return role,text

def phrase_questions(transcripts,meta,question_tpye,dataset,info):
	f = open('../data_files/data.pkl','rb')
	data = pickle.load(f)
	f.close()
	questions = pd.DataFrame(columns=["participantid","role","question","answer"])
	l1 = list(pd.to_numeric(data["ground_truth_opva"]["Extraversion_observer_facet_mean"]).round(2))
	l2 = list(pd.to_numeric(data["ground_truth_opva"]["Conscientiousness_observer_facet_mean"]).round(2))
	answers_list = ["Extraversion:"+str(ll1)+"\n"+"Conscientiousness:"+str(ll2) for ll1,ll2 in zip(l1,l2)]
	#for transcript in transcripts:
	for i in range(len(transcripts)):
		transcript = transcripts.loc[i]
		role,text = question(transcript,meta,question_tpye,dataset,info)
		df = pd.DataFrame([[transcript["participantid"],role,text,answers_list[i]]],
					columns = ["participantid","role","question","answer"])
		questions = pd.concat([questions,df],ignore_index=True)
	return questions

def save_questions(question_tpye,dataset,info):
	f = open('../data.pkl','rb')
	data = pickle.load(f)
	f.close()
	transcripts = data["transcripts_opva"]
	meta = 	data["meta_%s"%(dataset)]
	questions = phrase_questions(transcripts,meta,question_tpye,dataset,info)
	f = open('%s/finetuning_%s.pkl'%(dataset,question_tpye),'wb')
	pickle.dump(questions, f)
	f.close()
	
if __name__ == "__main__":	
	question_tpyes = ["factors","facets","facets_factors"]
	question_tpye = question_tpyes[0]
	dataset = "opva"
	info = True
	#for question_tpye in question_tpyes:
	save_questions(question_tpye,dataset,info)
	f = open("opva/finetuning_%s.pkl"%(question_tpye),"rb")
	q = pickle.load(f)
	f.close()
	train_dic = []
	with jsonlines.open('opva/train.jsonl', mode='a') as writer:
		for index, q_ in q.iterrows():
			t_dic_sys = {"role": "system","content": q_["role"]}
			t_dic_user = {"role": "user","content": q_["question"]}
			t_dic_ans = {"role": "assistant","content": q_["answer"]}
			t_dic = {"messages":[t_dic_sys,t_dic_user,t_dic_ans]}
			writer.write(t_dic)
		#train_dic.append(t_dic)
