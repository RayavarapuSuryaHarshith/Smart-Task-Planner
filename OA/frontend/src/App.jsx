import React, {useState, useEffect} from 'react'

export default function App(){
  const [goal, setGoal] = useState('Launch MVP in 14 days')
  const [due, setDue] = useState(14)
  const [out, setOut] = useState(null)
  const [plans, setPlans] = useState([])

  async function generate(){
    setOut('Thinking...')
    const res = await fetch('/plan', {method:'POST', headers: {'content-type':'application/json'}, body: JSON.stringify({goal, due_days: due})})
    const j = await res.json()
    setOut(JSON.stringify(j, null, 2))
  }

  async function save(){
    setOut('Saving...')
    const res = await fetch('/plan/save', {method:'POST', headers: {'content-type':'application/json'}, body: JSON.stringify({goal, due_days: due})})
    const j = await res.json()
    setOut(JSON.stringify(j, null, 2))
    await list()
  }

  async function list(){
    const res = await fetch('/plans')
    const j = await res.json()
    setPlans(j)
  }

  useEffect(()=>{list()}, [])

  return (
    <div style={{fontFamily:'Arial', padding:20}}>
      <h1>Smart Task Planner</h1>
      <div>
        <textarea value={goal} onChange={e=>setGoal(e.target.value)} style={{width:'100%',height:80}} />
        <div style={{marginTop:8}}>
          Due days: <input type='number' value={due} onChange={e=>setDue(parseInt(e.target.value||'0'))} />
        </div>
        <div style={{marginTop:8}}>
          <button onClick={generate}>Generate</button>
          <button onClick={save} style={{marginLeft:8}}>Save</button>
        </div>
      </div>
      <h2>Output</h2>
      <pre style={{background:'#f4f4f4', padding:12}}>{out || '(no output)'}</pre>

      <h2>Saved Plans</h2>
      <ul>
        {plans.map(p=> (
          <li key={p.id}><strong>{p.goal}</strong> — {p.due_days} days — {new Date(p.created_at).toLocaleString()}</li>
        ))}
      </ul>
    </div>
  )
}
