import os
import time
import json
import asyncio
from src.main import get_answer_by_gpt_with_pc_qa_context, get_answer_by_gpt_with_pc_summary_context
from src.utility import Answer, ReqData

qa_output_file = os.path.join('results', 'qa_results.json')
summary_output_file = os.path.join('results', 'summary_results.json')
failed_ques_file = os.path.join('results', 'failed_ques_file.json')

delay_between_tasks = 0.5  # Adjust the delay time here
timeout = 30  # Adjust the timeout here
max_parallel_tasks = 15  # Adjust the maximum number of parallel tasks here


async def process_questions_from_setA_and_save_results(context="qa"):
    setA_dir = "gpt/src/json_files/"
    json_files = [f for f in os.listdir(
        setA_dir) if f.endswith('.json') and 'setA' in f]

    results = []
    failed_ques = []

    # Limit the number of tasks currently running in parallel
    semaphore = asyncio.Semaphore(max_parallel_tasks)

    tasks = []
    for json_file in json_files:
        tasks.append(process_data_from_file(semaphore, setA_dir,
                     json_file, context == "qa", results, failed_ques))
    await asyncio.gather(*tasks)

    output_file = qa_output_file if context == "qa" else summary_output_file
    save_results(results, failed_ques, output_file)
    print(f"Results saved to {output_file}")


async def process_data_from_file(semaphore, setA_dir, json_file, context="qa", results=None, failed_ques=None):
    if results is None:
        results = []
    if failed_ques is None:
        failed_ques = []

    topic_name = json_file.split('_')[0]
    file_path = os.path.join(setA_dir, json_file)

    async with semaphore:
        try:
            await asyncio.wait_for(
                process_questions(semaphore, setA_dir, json_file,
                                  context, results, failed_ques),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(
                f"Task for file {json_file} exceeded the timeout of {timeout} seconds.")


async def process_questions(semaphore, setA_dir, json_file, context, results, failed_ques):
    with open(os.path.join(setA_dir, json_file), 'r') as f:
        data = json.load(f)

    os.makedirs('results', exist_ok=True)

    tasks = []
    for question_dict in data:
        # req_data = {'question': question_dict,
        #             'topic': json_file.split('_')[0]}
        answer = {"Answer": question_dict["answer"],
                  "Justification": question_dict["justification"]}
        expected_answer_instance = Answer(**answer)
        req_data = ReqData(topic=json_file.split('_')[
                           0], question=question_dict)
        result_func = get_answer_by_gpt_with_pc_qa_context if context == "qa" else get_answer_by_gpt_with_pc_summary_context
        task = asyncio.create_task(process_question(
            semaphore, req_data, expected_answer_instance, result_func, results, failed_ques))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def process_question(semaphore, req_data, expected_answer_instance, result_func, results, failed_ques):
    async with semaphore:
        result = result_func(req_data, answer_in_markdown_text=False)
    question = req_data.question.dict()
    print(question)
    if result['answer']:
        answer_instance: Answer = result['answer']
        answer = answer_instance.Answer[:1]
        # req_data_dict = req_data.__dict__()

        expected_answer = expected_answer_instance.Answer.replace(
            'Option', '').strip()
        is_correct = answer == expected_answer

        results.append({
            'question': question,
            'topic': req_data.topic,
            'result': answer_instance.dict(),
            'expected_answer': expected_answer,
            'generated_answer': answer,
            'is_correct': is_correct
        })
    else:
        failed_ques.append(question)
    await asyncio.sleep(delay_between_tasks)


def save_results(results, failed_ques, output_file):
    if results:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
    if failed_ques:
        with open(failed_ques_file, 'w') as f:
            json.dump(failed_ques, f, indent=4)


def count_correct_answers(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    correct_answers = sum(question["is_correct"] for question in data)
    total_questions = len(data)
    wrong_answers = total_questions - correct_answers

    print("Total questions:", total_questions)
    print("Correct answers:", correct_answers)
    print("Wrong answers:", wrong_answers)


if __name__ == "__main__":
    asyncio.run(process_questions_from_setA_and_save_results(context="qa"))
    asyncio.run(process_questions_from_setA_and_save_results(context="summary"))
