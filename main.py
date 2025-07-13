from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess
import time
import re
import os
from dotenv import load_dotenv 
load_dotenv() 

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])


from openai import OpenAI
client = OpenAI()
allMessages = [{"role": "developer", "content": 'You make test cases (inputs and expected outputs) given a certain description of what a piece of code is supposed to do. Ensure inputs and outputs are in Python (eg. "True" instead of "true" or "False" instead of "false"). Create at least 5 test cases (inputs and outputs) but go higher than that if possible. Create as many test cases as necessary to comprehensively test the code. Maintain accuracy in the expected outputs. Edge cases should also be included. Lastly, make sure to stay within any input restrictions (restrictions for what the input can be eg. letters only, numbers only, max length, min length, etc). Especially important is the datatype (String, Int, etc). Ensure that datatypes are consistent for test cases (eg. if input is specified to be a string, ensure all the inputs are string even if they are numerical (unless otherwise specified). Eg. if the user specifies string and your sample input is 123, write it as "123" instead). Opposite also applies, if the user specifies an integer/decimal, only return an int or decimal without quotes. Answer ONLY in the following valid JSON format: {"testCases": [{"inputs": ["sample inputs"], "output": "expected output"}...], "error": Any errors in code prompt (optional)}. Note: inputs must be an array and there may be multiple inputs (parameters) for a single test case. Keep the inputs an array even though it might just have one value in it (to represent one parameter). Do not include error attributes for individual test cases. Instead, have one error string outside the testCases array to report primarily code prompt errors if present. Make sure returned JSON is VALID and free from syntax errors. Ensure closing brackets are included. Include just the plain inputs and outputs with no code like .lower(), .replace(), or operations like * or +. Give the values themselves (eg. "aaaa" or 12 rather than "a" * 4 or 3 * 4). Ensure JSON syntax is valid and follows the given template. Above all else, ensure that ONLY a valid JSON object. No other extra text other than that. It should start and end with curly braces and only contain the JSON object within. Do not include an intro in text. Do not start or end with ```json or something similar. Just start with curly brackets and end with curly brackets.'}]
numberFiles = 0

@app.route('/createTestCases', methods=['POST'])
def createTestCases():

    # get test cases info
    testCasesInfo = request.get_json()

    attemptsLeft = 5

    prompt = testCasesInfo['purpose']

    # build the prompt based on user input restrictions
    if(testCasesInfo.get('stringOnly')):
        prompt += ". String only. "

        if(testCasesInfo.get('maxLength')):
            prompt += "Max length of string: " + testCasesInfo.get('maxLength') + ". "
        if(testCasesInfo.get('minLength')):
            prompt += "Min length of string: " + testCasesInfo.get('minLength') + ". "

    if(testCasesInfo.get('numbersOnly')):
        prompt += ". Int/decimal only. "

        if(testCasesInfo.get('maxValue')):
            prompt += "Max value of int/decimal: " + testCasesInfo.get('maxValue') + ". "
        if(testCasesInfo.get('minValue')):
            prompt += "Min value of int/decimal: " + testCasesInfo.get('minValue') + ". "

    if(testCasesInfo.get('regex')):
        prompt += "Adhere to the following regex: "  + testCasesInfo.get('regex') + ". "
    
    if(testCasesInfo.get('customInputRestrictions')):
        prompt += "Follow these custom restrictions: "  + testCasesInfo.get('customInputRestrictions') + "." 


    # attempt a max of 5 times to get a valid JSON object with the test cases
    while True:
        attemptsLeft -= 1

        if(attemptsLeft <= 0):
            return jsonify({"error": "Error generating test cases"})

        try:
            allMessages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages = allMessages,
            )

            message = completion.choices[0].message.content
            message = json.loads(message)

            # check if message JSON holds necessary information (testCases, inputs, outputs, etc) and matches input requirements
            if(not message.get("testCases")):
                prompt += "Make sure to adhere to the format specified"
                continue

            for i in range(len(message["testCases"]) - 1, -1, -1):

                if("inputs" in message["testCases"][i]):

                    for x in range(len(message["testCases"][i].get("inputs")) - 1, -1, -1):

                        if testCasesInfo.get('stringOnly') and type(message["testCases"][i]['inputs'][x]) != str:
                            message["testCases"].pop(i)
                            continue

                        if testCasesInfo.get('numbersOnly') and (type(message["testCases"]['inputs'][x]) != int or type(message["testCases"]['inputs'][x]) != float):
                            message["testCases"].pop(i)
                            continue

                        if testCasesInfo.get('stringOnly') and testCasesInfo.get('maxLength') and len(message["testCases"]['inputs'][x]) > testCasesInfo.get('maxLength'):
                            message["testCases"].pop(i)
                            continue
                        
                        if testCasesInfo.get('stringOnly') and testCasesInfo.get('minLength') and len(message["testCases"]['inputs'][x]) < testCasesInfo.get('minLength'):
                            message["testCases"].pop(i)
                            continue                    
                        
                        if testCasesInfo.get('numbersOnly') and testCasesInfo.get('maxValue') and message["testCases"]['inputs'][x] > testCasesInfo.get('maxValue'):
                            message["testCases"].pop(i)
                            continue

                        if testCasesInfo.get('numbersOnly') and testCasesInfo.get('minValue') and message["testCases"]['inputs'][x] < testCasesInfo.get('minValue'):
                            message["testCases"].pop(i)
                            continue

                        if testCasesInfo.get("regex") and re.fullmatch(testCasesInfo["regex"], str(message["testCases"]['inputs'][x])):
                            message["testCases"].pop(i)
                            continue                    
                
                elif ("input" in message["testCases"][i]):
                    message["testCases"][i]["inputs"] = message["testCases"][i].get("input")
                elif ("Input" in message["testCases"][i]):
                    message["testCases"][i]["inputs"] = message["testCases"][i].get("Input")
                elif ("Inputs" in message["testCases"][i]):
                    message["testCases"][i]["inputs"] = message["testCases"][i].get("Inputs")
                else:
                    print("inputs")
                    message["testCases"].pop(i)
                

                # check if output exist
                if(not "output" in message["testCases"][i]):
                    print("output")
                    if(message["testCases"][i].get("outputs")):
                        message["testCases"][i]["output"] = message["testCases"][i].get("outputs")
                    elif("Output" in message["testCases"][i]):
                        message["testCases"][i]["output"] = message["testCases"][i].get("Output")
                    elif("Outputs" in message["testCases"][i]):
                        message["testCases"][i]["output"] = message["testCases"][i].get("Outputs")
                    else:
                        message["testCases"].pop(i)
            
            if(len(message["testCases"]) < 5):
                prompt += " Ensure input restrictions are met (eg. max length, min length, string only, numbers only, etc) and ensure JSON syntax is correct."
                continue

            return jsonify(message)
        
        except:
            prompt += " Ensure JSON syntax is correct and ONLY the object is returned. DO NOT INCLUDE ANY EXTRA TEXT"

@app.route('/checkTestCase', methods=['POST'])
def checkTestCase():
    global numberFiles

    # get test case info
    testCaseInfo = request.get_json()
    inputs = testCaseInfo["testCase"]["inputs"]
    inputParameterStr = ""

    # create function call parameter list code based on type (string or int/float)
    if(type(inputs[0]) == str):
        for i in range(len(inputs)):
            if(i == 0):
                inputParameterStr = '"' + inputs[i] + '"'
            else:
                inputParameterStr += ", " + '"' + inputs[i] + '"'
    else:
        inputParameterStr = ", ".join(inputs)

    # create final code with function calls to test code against test cases
    finalCode = testCaseInfo["code"] + f"""
    
try:
    print(str({testCaseInfo["functionName"]}({inputParameterStr})))
except Exception as e:
    print("Error: " + str(e))
"""

    # save code to a file
    numberFiles += 1
    fileName = "pythonFile.py" + str(numberFiles)

    with open(fileName, "w") as f:
        f.write(finalCode)

    startTime = time.time()

    # try running the code and record any errors
    try:
        process = subprocess.run(["python", fileName], capture_output = True, text = True, timeout = 2)
        totalRuntime = time.time() - startTime
    
    except subprocess.TimeoutExpired:
        os.remove(fileName)
        return "Timeout expired"
    except Exception as e:
        os.remove(fileName)
        return "Error: " + str(e)
    
    # delete file once done
    os.remove(fileName)


    # if user code output doesn't match expected output, confirm correct output using ChatGPT and generate explanations for why the code failed 
    if(process.stdout.strip() !=  testCaseInfo["testCase"]["output"]):

        # try to get a valid JSON object with explanation/suggestions for code failure and confirmed correct output
        remainingAttempts = 5
        while True:

            remainingAttempts -= 1
            if remainingAttempts <= 0:
                return "Error generating explanation"
            
            try:    
                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages = [{"role": "developer", "content": 'You are an extremely professional programming assistant that helps concisely point out errors in code. Use a few brief sentences explaining the failure of the code if failure was identified. Speak objectively in passive voice. Given a prompt, input, output, expected output, and code, help reconcile why the code produced a different output than the expected output. Also determine what the correct output is (only if completely certain). Return your analysis in this exact JSON format (very important to use correct JSON syntax): {"explanation": "Brief explanation of why the code failed and how to fix it if you determined its output was incorrect. If output is determined to be correct, leave blank. If unable to accurately make code suggestions or point out errors, leave blank", "correctOutput": "Output you think is correct based on the prompt and input"}. Note, input will be an array containing the parameters passed (in order) to the function'},
                                {"role": "user", "content": "Function goal: " + str(testCaseInfo["testCase"]["inputs"]) + "; " +  "Input: " + str(testCaseInfo["testCase"]["inputs"]) + "; " + "Code Output: " + process.stdout.strip() + "; " + "Expected Output: " + testCaseInfo["testCase"]["output"] + "; " + "Code: " + testCaseInfo["code"]}
                                ],
                )

                message = completion.choices[0].message.content
                message = json.loads(message)
                return {"output": process.stdout.strip(), "correctOutput": message["correctOutput"], "explanation": message["explanation"], "totalRuntime": totalRuntime}
            
            except:
                pass
    else:
        return {"output": process.stdout.strip(), "correctOutput": process.stdout.strip(), "totalRuntime": totalRuntime}


if __name__ == '__main__':
    app.run(debug=True)