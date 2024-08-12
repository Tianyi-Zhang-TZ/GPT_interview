# -*- coding: utf-8 -*-

import pickle
import pandas as pd
import os
import re
import sys
import pickle
sys.path.append("..")
import prompt_p
import data_analysis
import json

def get_answers(question_tpye,dataset,model,infor,answer_list,cate):
	#answer_list = "output_data/%s/answers_%s_%s_%s/"%(model,dataset,question_tpye,"infor" if infor else "noninfor")
	filelist = os.listdir(answer_list)
	answers = []
	for file in filelist:
		try:
			filename =answer_list +file
			with open(filename) as f:
				txt = f.read()
			t = re.sub(r'\n+', '\n', txt)
			answers.append({"participantid":file[0:-4],"answer":t})
		except Exception as es:
			print(file)
			print(es)
	df = pd.DataFrame(answers)
	return df

def split_string(text):
  parts = text.split("Question 1")
  if len(parts) > 1:
    input_text = parts[1].split("Please answer with the template")[0] 
    return "Question 1"+input_text, parts[0] + "Please answer with the template"+parts[1].split("Please answer with the template")[1]
  else:
    return None, text

def get_questions(question_tpye,model,dataset,infor,cate):
	question_tpyes = ["factors","facets","factors_all","hirability","mean_facets","facets_factors"]
	n = question_tpyes.index(question_tpye)
	m = 0 if n>=4 else n
	mark = "" if cate else "_int"
	mark_infor = "_infor" if infor else "_noninfor"
	question_dir ='../%s/questions_%s%s%s.pkl'%(dataset,question_tpye,mark_infor,mark)
	with open("../data_files/data.pkl","rb") as f:
		data= pickle.load(f)
	with open("../data_files/select_columns.pkl","rb") as f:
		ssc = pickle.load(f)[dataset]
	if os.path.exists(question_dir):
		with open(question_dir, 'rb') as file:
				questions = pickle.load(file)
	else:
		questions = prompt_p.save_questions(question_tpye,dataset,infor,cate)
	answer_list = "output_data/%s/answers_%s_%s%s%s/"%(model,dataset,question_tpye,mark_infor,mark)
	df = get_answers(question_tpye,dataset,model,infor,answer_list,cate)
	df_questions = pd.merge(questions, df,on="participantid",how = "left")
	sc = ssc["sc"];sc_pre = ssc["sc_pre"]
	ground_truth = data["ground_truth_%s"%dataset]
	if not cate:
		ground_truth = data_analysis.convert_columns(ground_truth,sc)
		sc = [[[element + "_int" for element in sublist] for sublist in inner_list] for inner_list in sc]
		data["ground_truth_%s"%dataset] = ground_truth
	select_cols_tru = sc[m]
	select_col_pre =sc_pre [m]
	select_col_tru = select_cols_tru[0]
	gr = data["ground_truth_%s"%dataset]
	g = gr[[gr.columns[0]]+select_col_tru]
	g.columns = ["participantid"]+select_col_pre
	if not cate:
		score_dict = {0:'low',1:'medium',2:'high'}
		g[g.columns[1:]]=g[g.columns[1:]].apply(lambda x: x.map(score_dict))
		df_ratings = g.groupby('participantid').apply(lambda x: pd.DataFrame({'participantid': [x['participantid'].iloc[0]],'rating_string': ['\n'.join([f'{col}: {x[col].iloc[0]}' for col in select_col_pre])]}))
	else:
		df_ratings = g.groupby('participantid').apply(lambda x: pd.DataFrame({'participantid': [x['participantid'].iloc[0]],'rating_string': ['\n'.join([f'{col}: {str(x[col].iloc[0])}' for col in select_col_pre])]}))
	df_ratings = df_ratings.reset_index(drop=True)
	df = pd.merge(df_questions, df_ratings,on="participantid",how = "left")
	df_training = pd.DataFrame(columns = ['participantid','instruction','input','output'])
	df_training['participantid'] =df['participantid']
	df_training['input'], df_training['instruction'] = zip(*df["question"].apply(split_string))
	df_training['output'] =df['rating_string']+"\n"+df['answer']
	return df_training

def main():
	question_tpye = "factors"
	model = "gemma2"
	dataset = "prolific"
	infor = True
	cate = True
	mark_cate = "" if cate else "_int"
	mark_infor = "_infor" if infor else "_noninfor"
	df_training =get_questions(question_tpye,model,dataset,infor,cate)
	data_list = df_training[['instruction', 'input', 'output']].to_dict('records') 
	folder_name ="prompt_finetuning/%s/"%model
	os.makedirs(folder_name,exist_ok=True)
	save_dir = "prompt_finetuning/%s/%s_%s%s%s.json"%(model,dataset,question_tpye,mark_infor,mark_cate)
	with open(save_dir, 'w') as f:
		   json.dump(data_list, f, indent=4)

if __name__ == "__main__":
	main()