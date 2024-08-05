# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:29:28 2023

@author: S4
"""

import pickle
import pandas as pd
import os
import time

def check_subid(sub,sublist):
	#return a list of subjects within the validated subject list	
	if len(sub[sub.columns[0]][0])!=len(sublist[sublist.columns[0]][0]):
		#qList = ["q1","q2","q3","q4","q5","q6","q7","q8"]
		df = pd.DataFrame(columns=['participantid','q1','q2','q3','q4','q5','q6','q7','q8'])
		#questions are not stored per subject but per question per participants
		for s in list(sub[sub.columns[0]]):
			ss = s.split("_")
			participantID = ss[0]
			question = ss[1]
			if participantID in list(sublist[0]):
				if not participantID in list(df[df.columns[0]]):
					df.loc[len(df.index)] =[participantID,'','','','','','','','']
					df[question][len(df.index)-1] = sub[sub[sub.columns[0]].isin([s])]["text"].tolist()[0]
				else:
					df[question][len(df.index)-1] = sub[sub[sub.columns[0]].isin([s])]["text"].tolist()[0]
	else:
		#ratings are stored per subject, only need to filter those who are not in the list
		df = pd.DataFrame(columns=sub.columns)
		for s in list(sub[sub.columns[0]]):
			if (s in list(sublist[sublist.columns[0]])):
				df = df.append(sub[sub[sub.columns[0]].isin([s])])
	return df
	

def save_files():	
	transcripts = pd.read_csv('opva/opva_twoParts_transcription_appended_googleAPI.csv',usecols=[1,2])
	transcripts_prolific = pd.read_csv("prolific/transcripts.csv",usecols=[0,8])
	ground_truth = pd.read_csv('opva/OSFdata_n710_20230220.csv')
	subject_id = pd.read_csv('opva/opva_Time1_n685.csv',header=None)
	questions_key_facet = {'q1':'Social self-esteem','q2':'Organization','q3':'Social boldness',
					'q4':'Diligence','q5':'Sociability','q6':'Perfectionism',
					'q7':'Liveliness','q8':'Prudence'}
	questions_key_personality = {'q1':'Extraversion','q2':'Conscientiousness','q3':'Extraversion',
					'q4':'Conscientiousness','q5':'Extraversion','q6':'Conscientiousness',
					'q7':'Extraversion','q8':'Conscientiousness'}
	questions = {'q1':"Remember a time when you were in a social setting where you didn't know any of the other people, and this affected the extent to which you felt (un)comfortable with yourself. Could you describe your personality in that situation? ",
				 'q2':"Remember a time when you finished using equipment at work and you could put everything back in place (or not). Could you describe your personality in that situation?  ",
				 'q3':"Remember a time when you took part in a group discussion and you could assume a listening or leading role. Could you describe your personality in that situation? ",
				 'q4':"Remember a time when a task was more challenging than usual and that you could decide to push yourself harder or leave it aside (or pass it to someone else). Could you describe your personality in that situation? ",
				 'q5':"Remember a time when you were invited to an after-work social event and you could decide to join or skip it. Could you describe your personality in that situation? ",
				 'q6':"Remember a time when a task required paying attention to details in order to avoid making mistakes. Could you describe your personality in that situation? ",
				 'q7':"Remember a time when your team members were feeling down and you could decide to raise their spirit (or not). Could you describe your personality in that situation? ",
				 'q8':"Remember a time when you wanted something badly at work and you could act on an impulse (or not) in order to get it. Could you describe your personality in that situation? "}
	meta_opva = {"num_questions":8,"num_factors":2, "num_facets":8, "num_generic":0,
			    	"questions_key_facet":{'q1':'Social self-esteem','q2':'Organization','q3':'Social boldness',
					'q4':'Diligence','q5':'Sociability','q6':'Perfectionism',
					'q7':'Liveliness','q8':'Prudence'},
					"questions_key_personality":{'q1':'Extraversion','q2':'Conscientiousness','q3':'Extraversion',
					'q4':'Conscientiousness','q5':'Extraversion','q6':'Conscientiousness',
					'q7':'Extraversion','q8':'Conscientiousness'},
				"questions":{'q1':"Remember a time when you were in a social setting where you didn't know any of the other people, and this affected the extent to which you felt (un)comfortable with yourself. Could you describe your personality in that situation? ",
				 'q2':"Remember a time when you finished using equipment at work and you could put everything back in place (or not). Could you describe your personality in that situation?  ",
				 'q3':"Remember a time when you took part in a group discussion and you could assume a listening or leading role. Could you describe your personality in that situation? ",
				 'q4':"Remember a time when a task was more challenging than usual and that you could decide to push yourself harder or leave it aside (or pass it to someone else). Could you describe your personality in that situation? ",
				 'q5':"Remember a time when you were invited to an after-work social event and you could decide to join or skip it. Could you describe your personality in that situation? ",
				 'q6':"Remember a time when a task required paying attention to details in order to avoid making mistakes. Could you describe your personality in that situation? ",
				 'q7':"Remember a time when your team members were feeling down and you could decide to raise their spirit (or not). Could you describe your personality in that situation? ",
				 'q8':"Remember a time when you wanted something badly at work and you could act on an impulse (or not) in order to get it. Could you describe your personality in that situation? "}
		}
	meta_prolific = {"num_questions":6,"num_factors":4, "num_facets":0, "num_generic":2,
					"questions_key_personality":{'q1':'Generic','q2':'Generic','q3':'Honesty-Humility',
					'q4':'Extraversion','q5':'Agreeableness','q6':'Conscientiousness'},
					'questions':{'q1'"What would you consider among your greatest strengths and weaknesses as an employee?"
				    'q2':"How would your best friend describe you?",
					'q3':"Think of situations when you made professional decisions that could affect your status or how much money you make. How do you usually behave in such situations? Why do you think that is?",
					'q4':"Think of situations when you joined a new team of people. How do you usually behave when you enter a new team? Why do you think that is?",
					'q5':"Think of situations when someone annoyed you. How do you usually react in such situations?  Why do you think that is?",
					'q6':"Think of situations when your work or workspace were not very organized. How typical is that of you? Why do you think that is?"}
		}
	transcripts_sort = check_subid(transcripts,subject_id)
	ground_truth_sort = check_subid(ground_truth,subject_id)
	f = open("data.pkl", 'wb')
	pickle.dump({"transcripts_opva":transcripts_sort,
			  "transcripts_prolific":transcripts_prolific,
			  "ground_truth_opva":ground_truth_sort,
			  "meta_opva":meta_opva,
			  "meta_prolific":meta_prolific},f)
	f.close()

def question(transcript,meta,question_tpye,dataset,info,cate):
	#question_tpye = "factors", "facets" (only for opva),"facets_factors","none","generic_only"(only for prolific)
	#dataset = "opva" or "prolific"
	#info =True, tell the AI what is this question is about
	num = meta["num_factors"] if (question_tpye == "factors" or question_tpye == 'facets_factors') else meta["num_facets"]
	t1 = "For each question, I can give you the indication (but not strongly constrained by) about what is the corresponding %s this question is related to. "%(question_tpye[0:-1] if question_tpye !="facets_factors" else "facect")
	t2 = "The person also answer 2 generic questions which do not relate to a specific factor of personality. You can also use this information to rate his or her personality."
	keys = ', '.join(list(set([i for i in meta["questions_key_personality"].values()]))) if (question_tpye == "factors" or question_tpye == 'facets_factors') else ', '.join(list(set([i for i in meta["questions_key_facet"].values()])))
	if cate:
		head = "You are a psychologist in personality research. Could you rate the personality score of the person based on the answer to the following questions? The personality score (ranging from 1.0-5.0) should be rated according to the HEXCO personality model by %s %s (i.e., %s). %s%s"%(num,question_tpye if question_tpye !="facets_factors" else "factors",
			keys,t1 if info else "", t2 if dataset=="prolific" and question_tpye!="generic_only" else "")
	else:
		head = "You are a psychologist in personality research. Could you rate the personality score of the person based on the answer to the following questions? The personality score (high/medium/low) should be rated according to the HEXCO personality model by %s %s (i.e., %s). %s%s"%(num,question_tpye if question_tpye !="facets_factors" else "factors",
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
		temp = temp + t+": rating (the rating should be 0/1/2, for high/medium/low respectively)\n"
	tail = "Please answer with the template:\n"+ temp + "and why. The rating should be overall ratings instead of for each question."
	#tail_ = "Please rate just 2 factors (i.e., Extraversion and Conscientiousness) instead of the 8 facets. "
	#if question_tpye == "facets_factors":
		#tail = tail_+ tail
	text = head +"".join(body)+tail
	return text

def phrase_questions(transcripts,meta,question_tpye,dataset,info,cate):
	questions = pd.DataFrame(columns=["participantid","question"])
	#for transcript in transcripts:
	for i in range(len(transcripts)):
		transcript = transcripts.loc[i]
		text = question(transcript,meta,question_tpye,dataset,info,cate)
		df = pd.DataFrame([[transcript["participantid"],text]],
					columns = ["participantid","question"])
		questions = pd.concat([questions,df],ignore_index=True)
	return questions

def save_questions(question_tpye,dataset,info,cate):
	mark = "" if cate else "_int"
	f = open('data.pkl','rb')
	data = pickle.load(f)
	f.close()
	transcripts = data["transcripts_opva"]
	meta = 	data["meta_%s"%(dataset)]
	questions = phrase_questions(transcripts,meta,question_tpye,dataset,info,cate)
	f = open('%s/questions_%s%s.pkl'%(dataset,question_tpye,mark),'wb')
	pickle.dump(questions, f)
	f.close()