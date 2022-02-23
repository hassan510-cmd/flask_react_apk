# stable_version
# App.js 
```js
  import logo from './logo.svg';
  import './App.css';
  import axios from 'axios';
  import { useState } from 'react';
  import 'bootstrap/dist/css/bootstrap.min.css';

  function App() {
    const [data, setData] = useState([])
    const getData = () => {
      axios.get("get").then((resp) => {
        console.log(resp.data.data)
        setData((prev)=>[...prev,resp.data.data])
      })
    }
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />

          <h1>Hi from python server</h1>

          <button className='btn btn-success' onClick={getData}>
            fetch from api
          </button>

          <div>
            {data.map((value,index) => (
                <li key={index} >
                    {value}
                </li>
            ))}

          </div>

        </header>
      </div>
    );
  }

  export default App;
```
