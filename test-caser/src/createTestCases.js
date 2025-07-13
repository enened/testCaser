import {useState} from "react";
import Axios from "axios"
import Header from "./header.js";
import TestCase from "./testCase.js";

function CreateTestCases(){
    const [purpose, setPurpose] = useState("")
    const [code, setCode] = useState("")
    const [functionName, setFunctionName] = useState("")
    const [stringOnly, setStringOnly] = useState(false)
    const [numbersOnly, setNumbersOnly] = useState(false)
    const [maxLength, setMaxLength] = useState()
    const [minLength, setMinLength] = useState()    
    const [maxValue, setMaxValue] = useState()
    const [minValue, setMinValue] = useState()
    const [regex, setRegex] = useState()
    const [customInputRestrictions, setCustomInputRestrictions] = useState()
    const [testCases, setTestCases] = useState([])
    const [numberCorrect, setNumberCorrect] = useState(0)
    const [loading, setLoading] = useState(false)

    const getFile = (e)=>{

        // Store text in file in code state
        if(e.target.files && e.target.files.length > 0){
            const reader = new FileReader()
            reader.readAsText(e.target.files[0])
            reader.onload = async (e) => { 
                const text = (e.target.result)
                setCode(text)
            };
        }
    }

    const createTestCases = (e)=>{
        e.preventDefault();
        
        // check if maxLength, minLength, maxValue, and minValue are all valid
        if(maxLength < minLength){
            alert("Max length specified is less than min length")
        }

        if(maxValue < minValue){
            alert("Max value specified is less than min value")
        }

        setLoading(true)

        // Generate test cases
        Axios.post("http://127.0.0.1:5000/createTestCases", {purpose: purpose, stringOnly: stringOnly, numbersOnly: numbersOnly, maxLength: maxLength, minLength: minLength, maxValue: maxValue, minValue: minValue, regex: regex, customInputRestrictions: customInputRestrictions}).then((response)=>{
            setLoading(false)
            if(response.data.error){
                alert(response.data.error)
            }
            else{
                setTestCases(response.data.testCases)
                setNumberCorrect(0)
            }
        })
    }

    return(
        <div>
            <Header/>
            
            <h2>Create test cases</h2>
            
            <form onSubmit={createTestCases}>
                <textarea rows={3} onChange={(e)=>{setPurpose(e.target.value)}} maxLength={5000} placeholder="Enter the purpose of your code (eg. reverse a string, check if string is a palindrome, etc)"></textarea>
                <br/>
                <textarea rows={20} onChange={(e)=>{setCode(e.target.value)}} maxLength={5000} placeholder="Enter python code to check against test cases" value={code}></textarea>
                <br/>
                <p>or</p>
                <label htmlFor = "codeFile" className="fileLabel">File</label>
                <input id="codeFile" type="file" accept=".py" onChange={getFile}/>
                <br/>
                <input style={{"maxWidth":"900px"}} type="text" onChange={(e)=>{setFunctionName(e.target.value)}} placeholder="Enter name of function to evaluate (eg. palindrome_checker, reverse_string, etc). Note: do not include the parentheses"/>
                <br/>

                
                <h3>Restrictions on test cases: </h3>

                <div className="flexRow">
                    {!numbersOnly && 
                        <div className="smallMargin">
                            <input type="checkbox" id="stringOnly" name="stringOnly" value="stringOnly" onChange={(e)=>{setStringOnly(e.target.checked)}}/>
                            <label htmlFor="stringOnly">String input</label>
                            <br/>

                            {stringOnly && 
                                <div>
                                    <input type="number" onChange={(e)=>{setMaxLength(e.target.value)}} placeholder="Max length"/>
                                    <br/>
                                    
                                    <input type="number" onChange={(e)=>{setMinLength(e.target.value)}}  placeholder="Min length"/>
                                    <br/>
                                </div>
                            }
                        </div>
                    }

                    {!stringOnly && 
                        <div className="smallMargin">
                            <input type="checkbox" id="numbersOnly" name="numbersOnly" value="numbersOnly" onChange={(e)=>{setNumbersOnly(e.target.checked)}}/>
                            <label htmlFor="numbersOnly">Integer/decimal input</label>
                            <br/>

                            {numbersOnly &&
                                <div>
                                    <input type="number" placeholder="Max value" onChange={(e)=>{setMaxValue(e.target.checked)}}/>
                                    <br/>
                                    
                                    <input type="number" placeholder="Min value" onChange={(e)=>{setMinValue(e.target.checked)}}/>
                                    <br/>
                                </div>
                            }

                        </div>
                    }
                </div>

                <input style={{"width": "90%", "maxWidth":"900px"}} type="text" placeholder="Regex" onChange={(e)=>{setRegex(e.target.checked)}}/>
                <br/>

                <input style={{"width": "90%", "maxWidth":"900px"}} type="text" placeholder="Extra constraints on test cases" onChange={(e)=>{setCustomInputRestrictions(e.target.checked)}}/>
                <br/>
                    
                <button type="submit">Generate test cases</button>
                
                {loading && <p>Loading...</p>}

                {testCases.length > 0 && <h5>Tests passed: {numberCorrect}/{testCases.length}</h5>}

                <table>

                    <thead>
                        {testCases.length > 0 &&
                            <tr>
                                <th>Input</th>
                                <th>Expected Output</th>
                                <th>Actual Output</th>
                                <th>Runtime</th>
                                <th>Notes</th>
                            </tr>
                        }
                    </thead>
                    
                    <tbody>
                        {testCases.length > 0 &&
                            testCases.map((val)=>{
                                return (
                                    <TestCase testCase={val} functionName = {functionName} code = {code} purpose = {purpose} setNumberCorrect = {setNumberCorrect}/>
                                )
                            })
                        }
                    </tbody>

                </table>

            </form>
        </div>
    )
}

export default CreateTestCases;