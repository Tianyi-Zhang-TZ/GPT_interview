# -*- coding: utf-8 -*-
import pickle
import pandas as pd
import os
import time


def question(transcript,meta,dataset,cate):
#cate boolen value, if True, regression, if False, classification
	info = None
	num = 6
	t2 = "The person also answer 2 generic questions which do not relate to a specific factor of personality. You can also use this information to rate his or her personality."
	keys = ['Communication flexibility','Persuasiveness','Quality orientation','Development orientation','Overall hireability']
	if cate:
		head = "You are a recruiter for a traineeship. Below is the post of the traineeship:\n A traineeship gives you real work experience with real responsibilities for a specified period of time. You will follow an intensive training program in your field, so you must be a highly motivated and hardworking person in order to qualify. Our goal is to create an innovative and dynamic environment - be part of this journey!  We are looking for you, if 1) You have a strong desire to develop yourself into a competitive professional. 2)you enjoy being around and working with people. 3) you have great presentation skills and enjoy taking the stage. 4) you don’t mind taking the lead and have strong leadership characteristics. 5)you are a good communicator and you are a team player. \n Traineeships are usually full-time for a period of 12 to 18 months. However, shorter programs are also available from 5 months on. There are no specific start dates for a traineeship at ‘Aurélien’, you can start throughout the entire year. Upon acceptance, we will offer a traineeship with a duration of 5-18 months. At Aurélien we pride ourselves on using modern personnel selection methods. Applying for our traineeships is easy. The first step is completing a video interview and personality questionnaire. We will contact you within a week about the outcome of the selection procedure.\n Please rate the job-related competencies (from 1.0-5.0) for the interviewee based on the answers in their interview: Communication flexibility (i.e., the ability to convey a message in different ways, depending on perceptions and responses); Persuasiveness (i.e., gaining acceptance of, or agreement with, a standpoint from others through a well-considered use of arguments, personal authority and/or diplomacy); Quality orientation (i.e., making an effort to deliver high-quality work, focusing on achieving or exceeding the established quality standards in one's own work and performance or that of others); and Development orientation (i.e., exerting oneself in order to broaden and deepen knowledge and skills and to gain new experiences in order to grow professionally and increase the quality of one’s own work). Additionally, please also rated ‘overall hireability’, defined as the extent to which the candidate would be able to fulfill the requirements of the management traineeship position.  "
	else:
		head = "You are a recruiter for a traineeship. Below is the post of the traineeship:\n A traineeship gives you real work experience with real responsibilities for a specified period of time. You will follow an intensive training program in your field, so you must be a highly motivated and hardworking person in order to qualify. Our goal is to create an innovative and dynamic environment - be part of this journey!  We are looking for you, if 1) You have a strong desire to develop yourself into a competitive professional. 2)you enjoy being around and working with people. 3) you have great presentation skills and enjoy taking the stage. 4) you don’t mind taking the lead and have strong leadership characteristics. 5)you are a good communicator and you are a team player. \n Traineeships are usually full-time for a period of 12 to 18 months. However, shorter programs are also available from 5 months on. There are no specific start dates for a traineeship at ‘Aurélien’, you can start throughout the entire year. Upon acceptance, we will offer a traineeship with a duration of 5-18 months. At Aurélien we pride ourselves on using modern personnel selection methods. Applying for our traineeships is easy. The first step is completing a video interview and personality questionnaire. We will contact you within a week about the outcome of the selection procedure.\n Please rate the job-related competencies (high/medium/low) for the interviewee based on the answers in their interview: Communication flexibility (i.e., the ability to convey a message in different ways, depending on perceptions and responses); Persuasiveness (i.e., gaining acceptance of, or agreement with, a standpoint from others through a well-considered use of arguments, personal authority and/or diplomacy); Quality orientation (i.e., making an effort to deliver high-quality work, focusing on achieving or exceeding the established quality standards in one's own work and performance or that of others); and Development orientation (i.e., exerting oneself in order to broaden and deepen knowledge and skills and to gain new experiences in order to grow professionally and increase the quality of one’s own work). Additionally, please also rated ‘overall hireability’, defined as the extent to which the candidate would be able to fulfill the requirements of the management traineeship position.  "
	head = head+"\n"
	qList = ["q%s"%(i) for i in range(1,len(meta["questions"])+1)]
	body = []
	for q in qList :
		txt = "Question %s: %s\nAnswer: %s\n"%(q[1],meta["questions"][q],transcript[q])
		body.append(txt)
	#tail = "Please answer with the template of ratings: \n and why."
	tt = keys
	#tt = list(set([i for i in meta["questions_key_personality"].values()])) if (question_tpye == "factors" or question_tpye == 'facets_factors') else list(set([i for i in meta["questions_key_facet"].values()]))
	temp = ""
	for t in tt:
		temp = temp + t+": rating (the rating should be 2/1/0, for high/medium/low respectively) \n"
	tail = "Please answer with the template:\n"+ temp + "and why. The rating should be overall ratings instead of for each question."
	#tail_ = "Please rate just 2 factors (i.e., Extraversion and Conscientiousness) instead of the 8 facets. "
	#if question_tpye == "facets_factors":
		#tail = tail_+ tail
	text = head +"".join(body)+tail
	return text

def phrase_questions(transcripts,meta,dataset,cate):
	questions = pd.DataFrame(columns=["participantid","question"])
	#for transcript in transcripts:
	for i in range(len(transcripts)):
		transcript = transcripts.loc[i]
		text = question(transcript,meta,dataset,cate)
		df = pd.DataFrame([[transcript["participantid"],text]],
					columns = ["participantid","question"])
		questions = pd.concat([questions,df],ignore_index=True)
	return questions

def save_questions(dataset,cate):
	f = open('data.pkl','rb')
	data = pickle.load(f)
	f.close()
	transcripts = data["transcripts_opva"]
	meta = 	data["meta_%s"%(dataset)]
	questions = phrase_questions(transcripts,meta,dataset,cate)
	f = open('%s/questions_%s_infor.pkl'%(dataset,"hirability"),'wb')
	pickle.dump(questions, f)
	f.close()