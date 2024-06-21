# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:29:28 2023

@author: S4
"""

import pickle
import pandas as pd
import os
import chatgtp4_test as gpt
#import gpt_4_test as gpt
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
	transcripts = pd.read_csv('../opva/opva_twoParts_transcription_appended_googleAPI.csv',usecols=[1,2])
	transcripts_prolific = pd.read_csv("../prolific/transcripts.csv",usecols=[0,8])
	ground_truth = pd.read_csv('../opva/OSFdata_n710_20230220.csv')
	subject_id = pd.read_csv('../opva/opva_Time1_n685.csv',header=None)
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
					'questions':{'q1':"What would you consider among your greatest strengths and weaknesses as an employee?",
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

def phrase_ground_truth(transcript,data,question_tpye,dataset):
	#g_d: the list for col names of the ground truth, [Extraversion, Conti]
	question_tpyes = ["factors","facets","factors_all","hirability","mean_facets"]
	n = question_tpyes.index(question_tpye)
	m = 0 if n>=4 else n
	d2 = data["ground_truth_%s"%dataset].columns
	ground_truth = data["ground_truth_%s"%dataset]
	sc = [ [["Extraversion_observer_facet_mean","Conscientiousness_observer_facet_mean"],#observer reported
		      ["extra10","consc10"]],#self-reported 
		   [d2[188:196],d2[118:126],d2[134:142], d2[150:158], d2[166:174],d2[444:452]],#facets
		   [d2[182:188],d2[112:118]],#all factors, mean_observer_rating, self-rating
		   [d2[210:215]]]#hirablity score		
	sc_pre = [["Extraversion","Conscientiousness"],
		  ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism'],
		  ["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"],
		  ['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']]
	select_col_tru = sc[m][0]
	select_col_pre =sc_pre [m]
	tru_data = ground_truth[["workerId"]+select_col_tru]
	t = tru_data[tru_data["workerId"]==transcript["participantid"]]
	text = []
	for i in range(1,t.shape[1]):
		text.append("%s for %s"%(str(round(float(t.iloc[0,i]),1)),select_col_pre[i-1]))
	return ", ".join(text)
	
def question(transcript,data,question_tpye,dataset,infor):
	#question_tpye = "factors", "facets" (only for opva),"mean_facets","none","generic_only"(only for prolific)
	#dataset = "opva" or "prolific"
	#infor =True, tell the AI what is this question is about
	ratings = phrase_ground_truth(transcript,data,question_tpye,dataset)
	meta = data["meta_%s"%(dataset)]
	num = meta["num_factors"] if (question_tpye == "factors" or question_tpye == 'mean_facets') else meta["num_facets"]	
	t1 = "For each question, I can give you the indication about what is the corresponding %s this question is related to. "%(question_tpye[0:-1] if question_tpye !="mean_facets" else "facect")
	t2 = "The person also answer 2 generic questions which do not relate to a specific factor of personality. You can also use this information to rate his or her personality."
	keys = ', '.join(list(set([i for i in meta["questions_key_personality"].values()]))) if (question_tpye == "factors" or question_tpye == 'mean_facets') else ', '.join(list(set([i for i in meta["questions_key_facet"].values()])))
	head = "You are a psychologist in personality research. This individual was rated %s based on his/her answers to following questions. Could you first analyze the individual’s answers and then explain why he/she was rated like this? The personality scores (ranging from 1.0-5.0) were rated according to the HEXACO personality model by %s %s (i.e., %s). %s%s"%(ratings,num,question_tpye if question_tpye !="mean_facets" else "factors",
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

def phrase_questions(transcripts,data,question_tpye,dataset,infor):
	questions = pd.DataFrame(columns=["participantid","question"])
	#for transcript in transcripts:
	for i in range(len(transcripts)):
		transcript = transcripts.loc[i]
		text = question(transcript,data,question_tpye,dataset,infor)
		df = pd.DataFrame([[transcript["participantid"],text]],
					columns = ["participantid","question"])
		questions = pd.concat([questions,df],ignore_index=True)
	return questions

def save_questions(question_tpye,dataset,infor):
	f = open('data.pkl','rb')
	data = pickle.load(f)
	f.close()
	transcripts = data["transcripts_opva"]
	questions = phrase_questions(transcripts,data,question_tpye,dataset,infor)
	f = open('%s/questions_%s.pkl'%(dataset,question_tpye),'wb')
	pickle.dump(questions, f)
	f.close()

def main(question_tpye,dataset,infor):
	folder_name = "output_data/gpt-4/answers_%s_%s_%s/"%(dataset,question_tpye,"infor" if infor else "noninfor")
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
				answer = gpt.get_answer(questions["question"][i])
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
	#for question_tpye in question_tpyes:
	save_questions(question_tpye,dataset,infor)
	f = open("opva/questions_%s.pkl"%(question_tpye),"rb")
	q = pickle.load(f)
	f.close()
	main(question_tpye,dataset,infor)
	'''
	dataset = "opva"
	predict = get_answers(question_tpye,dataset)   
	f = open("output_data/pre_opva_factors_infor.pkl",'wb')
	pickle.dump(predict,f)
	f.close()
	'''
