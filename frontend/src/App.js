import './App.css';
import { useState, useEffect } from 'react'
import json from './data/vist.jsonl'
import {
  HashRouter,
  Routes,
  Route,
  useParams,
  useNavigate,
} from "react-router-dom";

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/:album_id" element={<Album/>} />
        <Route path="/" element={<Album/>} />
      </Routes>
    </HashRouter>
  );
}

export default App;

function Album() {
  const [data, setData] = useState([])
  const [random_data, setRandom_data] = useState(null)
  const { album_id } = useParams()
  const navigate = useNavigate()

  async function get_data() {
    const response = await fetch(json)
    const data = await response.json()
    setData(data)
  }

  const get_random_data = async (random=false) => {
    let id = album_id ? album_id : -1
    if (random) {
      id = -1
    }
    const ids = Object.keys(data)
    console.log(id, ids)
    if (id === -1) {
      id = ids[Math.floor(Math.random() * ids.length)]
    }
    // console.log(id, album_id)
    const rdata = data[id]
    // console.log(rdata)
    for (let i=0; i < rdata['sis'].length; i += 1) {
      const img_url = rdata['sis'][i]['img_url']
      let dii = ''
      for (let j=0; j < rdata['dii'].length; j += 1) {
        if (rdata['dii'][j]['img_url'] == img_url) {
          dii = rdata['dii'][j]['text']
          break
        }
      }
      rdata['sis'][i]['dii'] = dii
    }
    // console.log("dd", rdata)
    if (rdata) {
      setRandom_data(rdata)
      navigate(`/${rdata.album_id}`)
      // window.history.replaceState(null, '', `/VIST-vis/${rdata.album_id}`)
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
        {random_data['sis'].map((item) => (
          <td><img id="context_img" src={item.img_url} width="200" alt={item.text} /></td>
        ))}
      </tr>
      {/* DII Text */}
      <tr>
        {random_data['sis'].map((item) => (
          <td>{item.dii}</td>
        ))}
      </tr>
      {/* SIS Text */}
      <tr>
        {random_data['sis'].map((item) => (
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
          {/* {get_table('dii')} */}
          {get_table('VIST-Visualizer')}
          <div style={{ margin: '40px' }}></div>
          <button onClick={() => get_random_data(true)}>Next</button>
        </>
        : null
      }
    </div>
  )
}