import React from 'react';

import axios from 'axios';
import './App.scss';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      files: [],
    };
    this.onFormSubmit = this.onFormSubmit.bind(this);
    this.onChange = this.onChange.bind(this);
    this.fileUpload = this.fileUpload.bind(this);
  }
  onFormSubmit(e) {
    e.preventDefault(); // Stop form submit
    this.fileUpload(this.state.file).then(response => {
      console.log(response.data);
    });
  }
  onChange(e) {
    Array.from(e.target.files).forEach(file => this.fileUpload(file))
  }
  fileUpload(file) {
    const url =
      'https://us-central1-graphical-envoy-287420.cloudfunctions.net/upload';
    const formData = new FormData();
    formData.append('file', file);
    const config = {
      headers: {
        'content-type': 'multipart/form-data'
      },
    };
    axios.post(url, formData, config).then((res) => {
      console.log(res)
    }).catch(err => console.log(err))
  }

  render() {
    return (
      <div>
        <div className='navbar'>
          <h1>smoothr</h1>
        </div>
        <p>Upload MP4 to smooth the FPS!</p>
        <form>
          <label class='custom-file-upload'>
            <input type='file' onChange={this.onChange}/>
            Upload
          </label>
        </form>
      </div>
    );
  }
}

export default App;
