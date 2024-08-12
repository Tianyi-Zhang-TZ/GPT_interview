# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:39:35 2024

@author: zty
"""
import pickle

f = open("data.pkl",'rb')
data = pickle.load(f)
f.close()
d2 = data["ground_truth_opva"].columns
d3 = data["ground_truth_prolific"].columns

sc = {"opva":{"sc":[ [["Extraversion_observer_facet_mean","Conscientiousness_observer_facet_mean"],#observer reported
			  ["extra10","consc10"]],#self-reported 
			[d2[188:196],d2[118:126],d2[134:142], d2[150:158], d2[166:174],d2[444:452]],#facets
			[d2[182:188],d2[112:118]],#all factors, mean_observer_rating, self-rating
			[d2[210:215]]],#hirablity score
		      "sc_pre":[["Extraversion","Conscientiousness"],
			  ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism'],
			  ["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"],
			  ['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']]
			  },
   "prolific":{"sc":[[['A_observer','C_observer','H_observer','E_observer'],['A_self', 'C_self', 'H_self','E_self']],
			[],
			[d3[17:23],d3[11:17]],#all factors
			[d3[23:29],d3[29:]]#generic and persoanlity question ratings
			],
			"sc_pre":[["Agreeableness","Conscientiousness","Honesty-Humility","Extraversion"],
	   [],["Honesty-Humility","Emotionality","Extraversion","Agreeableness","Conscientiousness","Openness to Experience"]]}}
with open("select_columns.pkl","wb") as f:
	pickle.dump(sc, f)





