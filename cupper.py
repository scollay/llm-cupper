import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

import models as models
import prompts as prompts


#=== Define paths
path_content = Path("../content")
path_content.mkdir(exist_ok=True)

path_graded = Path("../graded")
path_graded.mkdir(exist_ok=True)


#=== Enter API key
openrouter_api_key = 'sk-999999999999999999999999'


#=== Indicators to run
topics = ["Simple Moving Average", "T3", "Bollinger Bands", "Coppock Curve",  "Clenow Momentum"]


#=== Models to run
test_models = list(models.test_models)
grader_models = list(models.grader_models)



#=== Step 1 - for each indicator, generate content with test model, then grade it with each grader model

for topic in topics:

	for test_model in test_models:

		#--- Set content file name
		code = models.test_models[test_model]['model_code']
		content_file = path_content / f"{topic}___{test_model.replace('/','_')}_{code}_content.md"


		#--- Generate content (skip if already exists)
		if content_file.exists():
			print(f"\nSkipping content generation for {topic} with test_model: {test_model} - output already exists")
		else:
			print(f"\nGenerating content for {topic} with test_model: {test_model}")

			content_prompt = prompts.content_prompt.replace("{topic}", topic)
			content, timer_secs, tokens_in, tokens_out = models.call_llm(prompt=content_prompt, model=test_model, openrouter_api_key=openrouter_api_key, temperature=0.2)
			test_run_info = models.make_test_run_info(topic=topic, model=test_model, timer_secs=timer_secs, tokens_in=tokens_in, tokens_out=tokens_out)

			content_file.write_text(content + "\n" + test_run_info)


		#--- Load content text that we want to grade
		content_text = content_file.read_text()
		test_run_info = "\n".join(content_text.splitlines()[-3:]) # json output from the run


		#--- Grade with each grader model (multi-threaded)
		def grade_one(grader_model):

			graded_file = path_graded / f"{topic}___{test_model.replace('/','_')}___gradedby___{grader_model.replace('/','_')}.md"

			if graded_file.exists():
				print(f"Skipping grading for {topic} with test_model: {test_model} grader_model:{grader_model} - output already exists")
				return
			else:
				print(f"Grading for {topic} with test_model: {test_model} grader_model: {grader_model}")


			grader_prompt = prompts.grader_prompt.replace("{content_prompt}", prompts.content_prompt).replace("{content_text}", content_text)


			try:
				content, timer_secs, tokens_in, tokens_out = models.call_llm(prompt=grader_prompt, model=grader_model, openrouter_api_key=openrouter_api_key, temperature=0)
			except Exception as e:
				print(f"ERROR grading test_model:{test_model} grader_model:{grader_model} - {type(e).__name__}: {e} - waiting 5s then trying again")
				time.sleep(5)
				try:
					print(f"\nGrading for test_model:{test_model} grader_model:{grader_model}")
					content, timer_secs, tokens_in, tokens_out = models.call_llm(prompt=grader_prompt, model=grader_model, openrouter_api_key=openrouter_api_key, temperature=0)
				except Exception as e:
					print(f"ERROR grading test_model:{test_model} grader_model:{grader_model} - {type(e).__name__}: {e} - skipping")
					return


			test_model_info = f"```json\n{json.dumps(models.test_models[test_model])}\n```"

			graded_output = f"{content}\n\n{test_model_info}\n\n{test_run_info}"

			graded_file.write_text(graded_output)

		with ThreadPoolExecutor(max_workers=8) as ex:
			list(ex.map(grade_one, grader_models))



#=== Step 2 - read all graded files into a dataframe

rows = []
for graded_file in path_graded.glob('*___gradedby___*.md'):

	if not graded_file.is_file():
		continue

	text = graded_file.read_text()
	json_blocks = re.findall(r'```json\s*\n(.*?)\n```', text, re.DOTALL)

	row = {}
	for block in json_blocks[-3:]:
		try:
			row.update(json.loads(block))
		except json.JSONDecodeError as e:
			print(f"WARN: bad JSON in {graded_file.name}: {e}")

	name_part, grader_part = graded_file.stem.split('___gradedby___')
	topic_part, _, model_part = name_part.partition('___') #filename starts with "{topic}___{model_with_/_replaced_by__}"
	row['model_name'] = model_part.replace('_', '/', 1)
	row['graded_by_model'] = grader_part.replace('_', '/', 1)
	rows.append(row)

df = pd.DataFrame(rows)
df = df.sort_values(['topic', 'model_name', 'graded_by_model']).reset_index(drop=True)

#=== Step #3 - score each row and write to a .csv file
df['total_score'] = df['scores'].apply(lambda s: s['clarity'] + s['accuracy']*2 + s['depth'] + s['adherence'] + s['code']*2 if isinstance(s, dict) else None) #accuracy & code count double; max 21 per juror (3+6+3+3+6)
df['total_score_perc'] = df['total_score'] / 21 #normalize to 0-1 (scores are 0-3, so min total is 0)

column_order = ['topic', 'model_name', 'model_code', 'graded_by_model', 'scores', 'total_score', 'total_score_perc', 'flags', 'summary', 'timer_secs', 'tokens_in', 'tokens_out', 'cost_tokens_in', 'cost_tokens_out', 'cost_tokens_tot', 'cost_in_per_million', 'cost_out_per_million', 'class', 'cost', 'country']
df = df[[c for c in column_order if c in df.columns]]
df.to_csv(path_graded / '_grading_results_each_run.csv', index=False)

#--- print for inspection
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print('\n', df.head(100))
print("\n", df.iloc[0])


#=== Step #4 - create summary view used to create article exhibits

#--- the two dots in the quality exhibit, on a 0-100 scale
df['writing_pct'] = df['scores'].apply(lambda s: (s['clarity'] + s['accuracy'] + s['depth'] + s['adherence']) / 4 / 3 * 100)  # mean of the 4 non-code criteria
df['coding_pct']  = df['scores'].apply(lambda s: s['code'] / 3 * 100)
df['grade_pct']   = df['total_score_perc'] * 100  # the bar

#--- actual generation cost per article, in cents.
#--- cost_tokens_tot repeats across the 3 grader rows for a given (model, topic), so drop those dupes before averaging
cents = (df.drop_duplicates(['model_name', 'topic'])
           .groupby('model_name')['cost_tokens_tot'].mean() * 100).rename('cents_per_article')

#--- one row per model, averaged across the 5 topics and 3 graders, sorted best-to-worst
#--- note: agg key is 'model_class' because 'class' is a reserved Python keyword
summary = (df.groupby('model_name')
             .agg(model_class=('class', 'first'),
                  country=('country', 'first'),
                  cost_in=('cost_in_per_million', 'first'),
                  cost_out=('cost_out_per_million', 'first'),
                  grade=('grade_pct', 'mean'),
                  writing=('writing_pct', 'mean'),
                  coding=('coding_pct', 'mean'))
             .join(cents)
             .reset_index()
             .sort_values('grade', ascending=False)
             .reset_index(drop=True))

summary[['grade', 'writing', 'coding']] = summary[['grade', 'writing', 'coding']].round(0).astype(int)
summary['cents_per_article'] = summary['cents_per_article'].round(2)

#--- View 1 -> quality-breakdown exhibit (bar = grade; dots = writing & coding; label = $in / $out)
view_quality = summary[['model_name', 'model_class', 'cost_in', 'cost_out', 'grade', 'writing', 'coding']]

#--- View 2 -> average-cost-per-article exhibit
view_cost = summary[['model_name', 'model_class', 'grade', 'cents_per_article']]

pd.set_option('display.width', None)
pd.set_option('display.max_rows', 100)
print('\n=== quality breakdown ===\n', view_quality.to_string(index=False))
print('\n=== average cost per article ===\n', view_cost.to_string(index=False))

summary.to_csv(path_graded / '_model_summary.csv', index=False)



