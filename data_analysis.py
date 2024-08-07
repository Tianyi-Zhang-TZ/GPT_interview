# -*- coding: utf-8 -*-

import pickle
import pandas as pd
import numpy as np
import os
import re
from sklearn.metrics import r2_score, accuracy_score,mean_absolute_error
from scipy.stats import pearsonr
import warnings

warnings.filterwarnings("ignore")

def find_all_indexes(A, B):
	indexes = []
	start = 0
	while True:
		index = A.lower().find(B.lower(), start)
		if index == -1:
			break
		indexes.append(index)
		start = index + 1
	return indexes

def is_decimal(s):
	pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$'
	return bool(re.match(pattern, s))

def find_closest_num(A, B): 
	indexes = find_all_indexes(A,B)
	
	for index in indexes:
		index = index+len(B)
		num = []
		while (len(num)<3 and index<len(A)):
			if A[index].isdigit() or A[index] == '.':
				num.append(A[index])
			index = index+1
		c_num = "".join(num)
		if is_decimal(c_num):
			if float(c_num)>5:
				closest_num = float(c_num[0])
			else:	
				closest_num = float(c_num)
			break
		elif is_decimal(c_num[0]):
			closest_num = float(c_num[0])
			break
		else:
			continue
		break
	return closest_num

def find_closest_num2(A, B): 
	indexes = find_all_indexes(A,B)
	for index in indexes:
		index = index+len(B)
		num = []
		while len(num)<1:
			if A[index].isdigit():
				num.append(A[index])
			index = index+1
		c_num = int(num[0])
		break
	return c_num

def find_closest_num3(A,B):
	score_dict = {'low': 0,'medium': 1,'high': 2}
	lines = A.split('\n')
	c_num = np.nan
	for line in lines:
		if B in line:
			for level in score_dict:
				if level in line.lower():
					c_num = score_dict[level]
	if c_num == np.nan:
		print("error")
	return c_num

def get_answer(filename,question_tpye,dataset,data,cate):
	meta = data["meta_%s"%dataset]
	if question_tpye == "factors_all":
		keys = ["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"]
	elif question_tpye == "hirability":
		keys = ['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']
	else:
		keys = list(set([i for i in meta["questions_key_personality"].values()])) if question_tpye == "factors" or question_tpye == "facets_factors" else list(set([i for i in meta["questions_key_facet"].values()]))
	if "Generic" in keys:
		keys.remove("Generic")
	f = open(filename)
	txt = f.read()
	f.close()
	init_value = [None for i in range(len(keys))]
	keys.insert(0,"participantid")
	sub_id = filename.split('/')[-1][0:-4]
	init_value.insert(0,sub_id)
	df = pd.DataFrame([init_value],columns=keys)
	for i in keys:
		g = txt.lower().find(i.lower())
		l = txt.find("sorry")
		if g != -1 and l==-1:
			if cate:
				if re.findall(r'\d+\.\d+|\d+', txt):
					pre = find_closest_num(txt,i)
					if pre >=5 or pre<1:
						pre = pre/2
					#pre = find_closest_num2(txt,i)#find_closest_num2 if the scores are int
					df.loc[0,i] = pre
				else:
					print(filename.split("/")[1])
			else:
				df.loc[0,i] = find_closest_num3(txt,i)

	return df

def get_answers(question_tpye,dataset,model,infor,answer_list,data,cate):
	#answer_list = "output_data/%s/answers_%s_%s_%s/"%(model,dataset,question_tpye,"infor" if infor else "noninfor")
	filelist = os.listdir(answer_list)
	df = pd.DataFrame()
	for file in filelist:
		try:
			df_sub = get_answer(answer_list+file,question_tpye,dataset,data,cate)
			df = pd.concat([df,df_sub],ignore_index=True)
		except Exception as es:
			print(file)
			print(es)
	return df

def compare_metric(dataset,pre_dir,c_metric,select_col_pre,select_col_tru,data):
	#pre_dir: the path for the predicted valuses
	#c_metric = "r2" or "accuracy" or "MAE", if choose accuracy score, the answer will be round to interger
	#select_col_pre: the name of the columns selected for comparision ,prediction
	#select_col_tru: the name of the columns selected for comparision, ground truth
	f = open(pre_dir,"rb")
	predict = pickle.load(f)
	f.close()
	if predict.index[0] == 0:	
		predict.index = predict["participantid"]
	ground_truth = data["ground_truth_%s"%dataset][select_col_tru]
	ground_truth.index = data["ground_truth_%s"%dataset][data["ground_truth_%s"%dataset].columns[0]]
	predcitions = predict[select_col_pre]
	#predcitions.index = predict["participantid"]
	for i in range(len(select_col_pre)):		
		ground_truth.loc[:,select_col_tru[i]] = pd.to_numeric(ground_truth[select_col_tru[i]],errors='coerce')
		predcitions.loc[:,select_col_pre[i]] = pd.to_numeric(predcitions[select_col_pre[i]],errors='coerce')
	ground_truth = ground_truth.dropna()
	predcitions = predcitions.dropna()
	common_ids = ground_truth.index.intersection(predcitions.index)	
	tru_data = ground_truth.loc[common_ids,select_col_tru]
	pre_data = predcitions.loc[common_ids,select_col_pre]
	for i in range(len(select_col_pre)):
		if c_metric =='r2':
			m = r2_score(tru_data[select_col_tru[i]], pre_data[select_col_pre[i]])
			print("%s for %s = %s"%(c_metric,select_col_pre[i],round(m,3)))
		elif  c_metric =='accuracy':
			m = accuracy_score(tru_data[select_col_tru[i]].round(0), pre_data[select_col_pre[i]].round(0))
			print("%s for %s = %s%%"%(c_metric,select_col_pre[i],round(m*100,2)))
		elif c_metric =="mae":
			m = 1-mean_absolute_error(tru_data[select_col_tru[i]], pre_data[select_col_pre[i]])
			print("%s for %s = %s"%(c_metric,select_col_pre[i],round(m,3)))
		elif c_metric == "corr":
			m,n = pearsonr(pre_data[select_col_pre[i]],tru_data[select_col_tru[i]])
			print("------------------------------------")
			print("%s for %s = %s"%(c_metric,select_col_pre[i],round(m,3)))
			print("p-value for %s = %s"%(select_col_pre[i],round(n,3)))			
	return tru_data,pre_data,m

def save_predictions(dataset,pre_dir,out_dir,select_col_tru,select_col_pre,data):
	f = open(pre_dir,"rb")
	predict = pickle.load(f)
	f.close()
	if predict.index[0] == 0:	
		predict.index = predict["participantid"%dataset]
	ground_truth = data["ground_truth_%s"][select_col_tru]
	ground_truth.index = data["ground_truth_%s"%dataset]["workerId"]
	predcitions = predict[select_col_pre]
	#predcitions.index = predict["participantid"]
	for i in range(len(select_col_pre)):		
		ground_truth.loc[:,select_col_tru[i]] = pd.to_numeric(ground_truth[select_col_tru[i]],errors='coerce')
		predcitions.loc[:,select_col_pre[i]] = pd.to_numeric(predcitions[select_col_pre[i]],errors='coerce')
	ground_truth = ground_truth.dropna()
	predcitions = predcitions.dropna()
	common_ids = ground_truth.index.intersection(predcitions.index)	
	tru_data = ground_truth.loc[common_ids,select_col_tru]
	pre_data = predcitions.loc[common_ids,select_col_pre]
	d = pd.concat([tru_data,pre_data],axis=1)
	order = [d.columns[0],d.columns[2],d.columns[1],d.columns[3]]
	d = d[order]
	'''
	f = open(out_dir,"wb")
	pickle.dump(d,f)
	f.close()
	'''
	return d

def get_from_answers(dataset,question_tpye,model,infor,answer_list,data,cate):
	predict = get_answers(question_tpye,dataset,model,infor,answer_list,data,cate)
	ff = ("_").join(answer_list.split("/")[2].split("_")[1:])
	file_name =  "output_data/%s/pre_%s.pkl"%(model,ff)  
	f = open(file_name,'wb')
	pickle.dump(predict,f)
	f.close()
	return predict,file_name

def mean_facets(pre_data,out_dir):
	pre_data.index = pre_data["participantid"]
	pre_data = pre_data.drop(columns = ["participantid"])
	order = ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism']	
	pre_data = pre_data[order]
	x = pd.concat([pd.DataFrame(np.mean(pre_data.iloc[:,0:4],axis=1)),pd.DataFrame(np.mean(pre_data.iloc[:,4:8],axis=1))],axis=1)
	x.columns = ["Extraversion","Conscientiousness"]
	f = open(out_dir,"wb")
	pickle.dump(x,f)
	f.close()
	return x

def get_data(model,dataset,question_tpyes,n,infor,cate,data):#get the grond truth and predictions 
	question_tpye = question_tpyes[n] if n !=4 else "facets"
	answer_list = "output_data/%s/answers_%s_%s_%s%s/"%(model,dataset,question_tpye,"infor" if infor else "noninfor","" if cate else "_int")		
	if n !=4:
		pre_dir = "output_data/%s/pre_%s_%s_%s%s.pkl"%(model,dataset,question_tpye,"infor" if infor else "noninfor","" if cate else "_int")
		if os.path.exists(pre_dir):
			f = open(pre_dir,"rb")
			predicts = pickle.load(f)
			f.close()
		else:
			predicts,pre_dir = get_from_answers(dataset,question_tpye,model,infor,answer_list,data,cate)		
	else:
		#for mean of facets only
		pre_dir = "output_data/%s/pre_%s_%s_%s%s.pkl"%(model,dataset,"mean_facets","infor" if infor else "noninfor","" if cate else "_int")
		if os.path.exists(pre_dir):
			f = open(pre_dir,"rb")
			predicts = pickle.load(f)
			f.close()
		else:
			predictions,_ = get_from_answers(dataset,question_tpye,model,infor,answer_list,data,cate)	
			predicts = mean_facets(predictions,pre_dir)
	return predicts,pre_dir

def convert_columns(df):
	d2 = df.columns
	columns = ["Extraversion_observer_facet_mean","Conscientiousness_observer_facet_mean","extra10","consc10"]+list(d2[188:196])+list(d2[118:126])+list(d2[134:142])+list(d2[150:158])+list( d2[166:174])+list(d2[444:452])+list(d2[182:188])+list(d2[112:118])+list(d2[210:215])	
	df_cleaned = df.dropna(subset=columns)  # Remove rows with NaNs in the specified columns
	for col in columns:
		df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')  # Convert to numeric, coercing errors to NaN
		df_cleaned = df_cleaned.dropna(subset=[col])  # Drop rows where conversion to numeric resulted in NaN
		
		# Apply the transformation rules
		new_col_name = f"{col}_int"
		df_cleaned[new_col_name] = df_cleaned[col].apply(
			lambda x: 0 if 1 <= x < 2.5 else (1 if 2.5 < x <= 3.5 else (2 if 3.5 < x <= 5 else None))
		)
	
	return df_cleaned	
	
if __name__ == "__main__": 
	f = open("data.pkl",'rb')
	data = pickle.load(f)
	f.close()
	n = 0#question type
	metric = "r2"
	dataset = "prolific"
	question_tpyes = ["factors","facets","factors_all","hirability","mean_facets","facets_factors"]
	infor = True
	cate = True
	model = "gemma2"	
	m = 0 if n>=4 else n
	predicts,pre_dir = get_data(model,dataset,question_tpyes,n,infor,cate,data)
	ground_truth = data["ground_truth_%s"%dataset]
	#ground_truth = convert_columns(ground_truth)
	data["ground_truth_%s"%dataset] = ground_truth
	d2 = ground_truth.columns
	d = []
	if dataset == "opva":
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
		sc = [[]]
		sc_pre = [["Extraversion","Conscientiousness","Honesty-Humility","Agreeableness"],
			[],["Extraversion","Conscientiousness","Honesty-Humility","Agreeableness","Emotionality","Openness to Experience"]]
	if not cate:
		sc = [[[element + "_int" for element in sublist] for sublist in inner_list] for inner_list in sc]

	select_cols_tru = sc[m]
	select_col_pre =sc_pre [m]
	for r in range(len(select_cols_tru)):
		select_col_tru = select_cols_tru[r]
		try:
			truth_name = select_col_tru[0].split("_")
			truth_name = truth_name[0] if (truth_name[1] != "observers") and (truth_name[1] != "observer") else "Mean of observers"
		except:
			truth_name = "Self Observation"
		print ("=======\t=======\t=======\t=======\t=======")
		print("\n \t Compared with %s \t"%(truth_name))
		tru_data,pre_data,m = compare_metric(dataset,pre_dir,metric,select_col_pre,select_col_tru,data)
		out_dir = "pre_%s_%s.pkl"%(dataset,truth_name)
		d.append(save_predictions(dataset,pre_dir,out_dir,select_col_tru,select_col_pre,data))
		print("\n \t statistic for predictions \t")
		for j in range(len(select_cols_tru[r])):
			print("%s: mean = %s, std = %s"%(select_col_pre[j],np.round(np.mean(pre_data[select_col_pre[j]]),3),np.round(np.std(pre_data[select_col_pre[j]]),3)))		
		print("\n \t statistic for ground truth \t")
		for j in range(len(select_cols_tru[r])):
			print("%s: mean = %s, std = %s"%(select_col_pre[j],np.round(np.mean(tru_data[select_col_tru[j]]),3),np.round(np.std(tru_data[select_col_tru[j]]),3)))
		