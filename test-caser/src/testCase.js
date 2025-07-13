import {useState, useEffect} from "react";
import Axios from "axios"

function TestCase({testCase, functionName, code, purpose, setNumberCorrect}){
    const [actualOutput, setActualOutput] = useState("")
    const [analysis, setAnalysis] = useState("")
    const [correctOutput, setCorrectOutput] = useState("")
    const [totalRuntime, setTotalRuntime] = useState("")
    const [classname, setClassname] = useState("")
    const [inputs, setInputs] = useState("")

    useEffect(()=>{

        // check whether the user passed the test case. If not, get the explanation for why the test case failed. 
        Axios.post("http://127.0.0.1:5000/checkTestCase", {testCase: testCase, functionName: functionName, code: code, purpose: purpose}).then((response)=>{
            if(response.data.error){
                alert(response.data.error)
            }
            else{
                setActualOutput(response.data.output)
                setAnalysis(response.data.explanation)
                setCorrectOutput(response.data.correctOutput)
                setTotalRuntime(response.data.totalRuntime)

                if(response.data.correctOutput == response.data.output){
                    setClassname("correctRow")
                    setNumberCorrect((numCorrect)=>{return numCorrect + 1})
                }
                else{
                    setClassname("incorrectRow")
                }


            }
        })
    }, [])

    useEffect(()=>{
        
        // turns the inputs array into a string to display
        let inputsStr = testCase.inputs[0]
        for (let i = 1; i < testCase.inputs.length; i++) {
            inputsStr += ", " + testCase.inputs[i]
        }
        setInputs(inputsStr)
    }, [testCase.inputs])


    return(
        <tr className={classname}>
            <td>{"" + inputs}</td>
            <td>{correctOutput ? correctOutput : "" + testCase.output}</td>
            <td>{actualOutput ? actualOutput : "Running..."}</td>
            <td>{totalRuntime ? totalRuntime + " seconds" : "Running..."}</td>
            <td>{analysis}</td>
        </tr>
    )
}

export default TestCase;