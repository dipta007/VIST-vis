import './App.css';
import { useState, useEffect } from 'react'
import json from './data/vist.jsonl'
import {
  BrowserRouter,
  Routes,
  Route,
  useParams,
} from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/:album_id" element={<Album/>} />
        <Route path="/" element={<Album/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

function Album() {
  const [data, setData] = useState([])
  const [random_data, setRandom_data] = useState(null)
  const { album_id } = useParams()

  async function get_data() {
    console.log("data")
    const response = await fetch(json)
    const data = await response.json()
    console.log(data)
    setData(data)
  }

  const get_random_data = async () => {
    let id = album_id ? album_id : -1
    const ids = Object.keys(data)
    if (id === -1) {
      id = ids[Math.floor(Math.random() * ids.length)]
    }
    console.log(id, album_id)
    const rdata = data[id]
    console.log(rdata)
    if (rdata) {
      setRandom_data(rdata)
      window.history.replaceState(null, rdata.album_id, `/${rdata.album_id}`)
    }
  }

  useEffect(() => {
    get_data()
  }, [])

  useEffect(()=>{
    get_random_data()
  },[data])

  const get_table = (type) => (
    <><h2>{type}</h2><table>
      {/* Image */}
      <tr>
        {random_data[type].map((item) => (
          <td><img id="context_img" src={item.img_url} width="200" alt={item.text} /></td>
        ))}
      </tr>
      {/* Text */}
      <tr>
        {random_data[type].map((item) => (
          <td>{item.text}</td>
        ))}
      </tr>
    </table></>
  )

  return (
    <div className="App">
      {!random_data && <div>loading</div>}
      {random_data?.album_id ?
        <>
          {/* <h1><a href={`https://${random_data[0].url}`} target="_blank">URL</a>: {random_data[0].url.split('/')[1]}</h1> */}
          {get_table('dii')}
          {get_table('sis')}
          <div style={{ margin: '40px' }}></div>
          <button onClick={get_random_data}>Next</button>
        </>
        : null
      }
    </div>
  )
}