import './App.css';
import axios from 'axios';
import { useState, useEffect } from 'react'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useParams,
} from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/:album_id" element={<Album/>} />
        <Route path="/" element={<Album/>} />
      </Routes>
    </Router>
  );
}

export default App;

function Album() {
  const [random_data, setRandom_data] = useState(null)
  const { album_id } = useParams()

  const get_random_data = async () => {
    const id = album_id ? album_id : -1
    
    const data = await axios.get(`https://vist.herokuapp.com/api/vist/${id}`)
    if (data) {
      setRandom_data(data.data)
      window.history.replaceState(null, data.data.album_id, `/${data.data.album_id}`)
    }
  }

  useEffect(()=>{
    get_random_data()
  },[])

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