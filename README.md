# GPT Interview 说明文档

数据库具体细节及前期工作详见：

> Zhang, Tianyi, et al. "Can Large Language Models Assess Personality from Asynchronous Video Interviews? A Comprehensive Evaluation of Validity, Reliability, Fairness, and Rating Patterns." *IEEE Transactions on Affective Computing* (2024). 
>
> https://tianyi-zhang-tz.github.io/Tianyi-Zhang-TZ/papers/LLMs_Personality.pdf



## 0. opva数据库标签信息说明

### 0.1 人格标签信息

数据库中包含了685位被试对与8个问题[q1,q2...,q8]的回答，每个问题用于激发一种**人格子维度（facet）**。用户每回答一个问题，评分者对被试的一种**人格子维度**进行打分。每个分数的取值范围为[1.0,5.0]。

> ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism']

其中，前四个人格子维度的平均值，构成**Extraversion人格维度**（factor）的得分。后四个人格子维度的平均值，构成**Conscientiousness人格维度**（factor）的得分。

此外，数据库中还包含用户自己对**Extraversion**和**Conscientiousness**两个**人格维度**（factor）的自评分数。

### 0.2 面试表现标签信息

数据库中还包含有人力资源专家给用户评的**职业素养评分（job-related competencies）**，包括：

> ['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']

这5个标签与8个问题没有明确的一一对应关系。每个分数的取值范围为[1.0,5.0]。



## 1. 数据库主文件data.pkl 

字典文件，包含了5个变量

![image-20240621153528523](https://github.com/Tianyi-Zhang-TZ/GPT_interview/blob/main/readme_figures/image-20240621153528523.png)

### 1.1 ground_truth_opva

包含了所有685个被试的547个标签信息，其中重要的信息有：

> ```python
> with open('data.pkl', 'rb') as file:
>     ground_truth = pickle.load(file)
> ground_truth = data["ground_truth_opva"]
> d2 = ground_truth.columns
> ["Extraversion_observer_facet_mean","Conscientiousness_observer_facet_mean"]#他评人格分数，分别对应[Extraversion, Conscientiousness]
> ["extra10","consc10"] #自评人格分数, 分别对应[Extraversion, Conscientiousness]
> d2[188:196] #他评人格子维度分数，分别对应 ['Social self-esteem','Social boldness','Sociability','Liveliness','Organization','Diligence','Prudence','Perfectionism'] 八个子维度
> d2[210:215] #他评面试分数，分别对应['Development orientation','Communication flexibility','Persuasiveness','Quality orientation','Overall hireability']]
> ```

他评人格分数，自评人格分数，他评人格子维度分数，他评面试分数为本研究的**4种**标签。

### 1.2 meta_opva

包含了数据库的元信息，具体包括：

> - **questions**：字典文件，储存了每一个题目q_n对应的题目内容。
> - **questions_key_facet**：字典文件，储存了每一个题目q_n对应的**人格子维度**。
> - **questions_key_personality**：字典文件，存储了每一个题目q_n对应的**人格维度**。

### 1.3 transcripts_opva

pandas dataframe 文件，包含了685个被试回答8个问题的文本内容。被试的编号储存在第一列中。



## 2. 生成prompt

针对三个不同任务生成三种不同prompts:

> 1. 预测人格维度(factors)分数。
> 2. 预测人格子维度(facets)分数。
> 3. 预测职业素养(hirability)分数。

通过prompt_p.py 生成任务1，2的prompt。

> ```python
> import prompt_p as pp
> question_tpyes = ["factors","facets","facets_factors"]
> #factors:任务1，facets:任务2，facets_factors，任务1，且让LLMs通过先融合facets信息预测factors
> question_tpye = question_tpyes[0]
> dataset = 'opva'
> info = True #告知LLMs每个问题与内一个人格维度/子维度对应
> pp.save_questions(question_tpye,dataset,info)
> ```

通过prompt_h.py 生成任务3的prompt。

> ```python
> import prompt_p as ph
> question_tpye = 'hirability'
> ph.save_questions('opva')
> ```

prompt的组成格式如下：

**任务1，2：**

![image-20240621180748541](https://github.com/Tianyi-Zhang-TZ/GPT_interview/blob/main/readme_figures/image-20240621180748541.png)

**任务3：**

![image-20240621180817522](https://github.com/Tianyi-Zhang-TZ/GPT_interview/blob/main/readme_figures/image-20240621180817522.png)



## 3. 储存LLMs回答

LLMs输出的回答应按照以下格式储存：

> output_data/
>
> ├─model_name/ 比如gpt-4
>
> ​	├─answers_opva_“question_tpye”_infor/ 比如answers_opva_factors_infor
>
> ​		├──users_id.txt 比如5a0f7d84ff266c0001d209cc.txt
>
> ​		└── .....



## 4. 数据分析

data_analysis.py 用于输出不同任务的预测值的表现。详见:

> https://github.com/Tianyi-Zhang-TZ/LLMs_Personality



## 5. 几种Fine-tuning思路

### 5.1 输入为prompt, 回答直接为分数。

此处注意修改prompt，去掉问题中的why

> Extraversion: 3.5
>
> Conscientiousness: 4.5

可使用`GPT_interview/finetuning/prepare_finetuning.py`生成prompt。

### 5.2 输入为prompt, 回答为分数+解释分数的文本

先由gpt-4或者其他LLMs生成打分依据。生成**人格维度**和**人格子维度**的打分依据prompt 可以使用`GPT_interview/finetuning/opva_questions_generate.py`生成。

打分依据应按照如下格式保存：

> finetuning/
>
> ├─output_data_finetuning
>
> ​	├─model_name/ 比如gpt-4
>
> ​		├─answers_opva_“question_tpye”_infor/ 比如answers_opva_factors_infor
>
> ​			├──users_id.txt 比如5a0f7d84ff266c0001d209cc.txt
>
> ​			└── .....